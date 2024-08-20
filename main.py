#!/usr/bin/env python3

import argparse
import hashlib
import os
import struct
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from os import listdir
from os import path
from hdr_v1 import *
from hdr_v2 import *
from prebuilt import PrebuiltType
from prebuilt import PREBUILT_DIR
from prebuilt import PREBUILT_BIN
from pyhsslms import HssLmsPrivateKey
from pyhsslms import HssSignature
from typing import List

class FmcInfo:
    pass

class PrebuiltInfo:
    pass

def gen_fmc_info(fmc_path, fmc_svn) -> FmcInfo:
    fmc_info = FmcInfo()

    if not path.isfile(fmc_path):
        raise RuntimeError("cannot find FMC binary {}".format(fmc_path))

    f = open(fmc_path, "rb")

    fmc_info.svn = fmc_svn
    fmc_info.data = f.read()
    fmc_info.size = f.tell()
    fmc_info.dgst = hashlib.sha384(fmc_info.data).digest()

    f.close()

    return fmc_info

def gen_prebuilt_info(pb_dir, pb_bin) -> List[PrebuiltInfo]:
    pbs_info = []

    for pb_name in pb_bin:
        pb_path = pb_dir + pb_name;

        if not path.isfile(pb_path):
            raise RuntimeError("cannot find prebuilt binary {}".format(pb_path))

        f = open(pb_path, "rb")

        pbi = PrebuiltInfo()
        pbi.name = pb_name
        pbi.type = pb_bin[pb_name].value
        pbi.data = f.read()
        pbi.size = f.tell()
        pbi.dgst = hashlib.sha384(pbi.data).digest()

        pbs_info.append(pbi)

        f.close()

    return pbs_info

def gen_fmc_hdr_v1(fmc_info, pbs_info) -> FmcHdrV1:
    hdr = FmcHdrV1()

    hdr.set_fmc_size(fmc_info.size)

    for pbi in pbs_info:
        hdr.add_prebuilt(pbi.type, pbi.size)

    return hdr

def gen_fmc_hdr_v2(fmc_info, pbs_info,
                   ecc_key_idx, ecc_key, lms_key_idx, lms_key) -> FmcHdrV2:

    hdr = FmcHdrV2()

    hdr.set_fmc_svn(fmc_info.svn)
    hdr.set_fmc_size(fmc_info.size)
    hdr.set_fmc_digest(fmc_info.dgst)

    for pbi in pbs_info:
        hdr.add_prebuilt(pbi.type, pbi.size, pbi.dgst)

    # generate ECDSA384 signature
    if ecc_key is not None:
        pem_f = open(ecc_key, "rb")
        pem_d = pem_f.read()

        key = load_pem_private_key(pem_d, password=None)
        sig = key.sign(hdr.output_body(), ec.ECDSA(hashes.SHA384()))
        sig_r, sig_s = decode_dss_signature(sig)

        sig_r = sig_r.to_bytes(48, byteorder='big')
        sig_s = sig_s.to_bytes(48, byteorder='big')

        hdr.set_ecc_key_index(ecc_key_idx)
        hdr.set_ecc_signature(sig_r, sig_s)

    # generate LMS_signature (N24/H15/W4)
    if lms_key is not None:
        key = HssLmsPrivateKey(os.path.splitext(lms_key)[0])
        hss_sig_bytes = key.sign(hashlib.sha384(hdr.output_body()).digest())
        hss_sig_level = int.from_bytes(hss_sig_bytes[0 : 4], "big") + 1
        hss_sig = HssSignature.deserialize(hss_sig_bytes)

        # extract signature parameters
        sig_q = hss_sig.lms_sig.q
        sig_ots_type = hss_sig.lms_sig.lmots_sig.type
        sig_ots_C = hss_sig.lms_sig.lmots_sig.C
        sig_ots_y = b''.join(hss_sig.lms_sig.lmots_sig.y)
        sig_tree_type = int.from_bytes(hss_sig.lms_sig.type, "big")
        sig_tree_path = b''.join(hss_sig.lms_sig.path)

        # assemble signature byte array
        sig_bytes = b''
        sig_bytes += struct.pack("<L", sig_q)
        sig_bytes += sig_ots_type
        sig_bytes += sig_ots_C
        sig_bytes += sig_ots_y
        sig_bytes += struct.pack("<L", sig_tree_type)
        sig_bytes += sig_tree_path

        hdr.set_lms_key_index(lms_key_idx)
        hdr.set_lms_signature(sig_bytes)

    return hdr

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", metavar="IN", help="input FMC raw binary", required=True)
    parser.add_argument("--output", metavar="OUT", help="output FMC binary with header", required=True)
    parser.add_argument("--version", help="FMC header version", required=True, type=int, choices=range(1, 3))
    parser.add_argument("--svn", metavar="SVN", type=int, help="FMC security version number, Default=0", default=0)
    parser.add_argument("--ecc-key", metavar="KEY", help="ECDSA384 signing key (.pem)")
    parser.add_argument("--ecc-key-index", metavar="IDX", type=int, help="ECDSA384 signing key index hint, Default=0", default=0)
    parser.add_argument("--lms-key", metavar="KEY", help="LMS signing key (.prv)")
    parser.add_argument("--lms-key-index", metavar="IDX", type=int, help="LMS signing key index hint, Default=0", default=0)
    parser.add_argument("--verbose", help="show detail information", action="store_true", default=False)
    args = parser.parse_args()

    fmc_info = gen_fmc_info(args.input, args.svn)
    pbs_info = gen_prebuilt_info(PREBUILT_DIR, PREBUILT_BIN)

    if args.version == 1:
        hdr = gen_fmc_hdr_v1(fmc_info, pbs_info)
    elif args.version == 2:
        hdr = gen_fmc_hdr_v2(fmc_info, pbs_info,
                             args.ecc_key_index, args.ecc_key,
                             args.lms_key_index, args.lms_key)
    else:
        raise RuntimeError("invalid FMC header version={}".format(args.version))

    # generate final output: Header || FMC Binary || Prebuilt Binaries
    f = open(args.output, "wb")

    f.write(hdr.output(args.verbose))
    f.write(fmc_info.data)
    for pbi in pbs_info:
        f.write(pbi.data)

    f.close()

if __name__ == "__main__":
    main()
