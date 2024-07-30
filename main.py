#!/usr/bin/env python3

import argparse
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from os import listdir
from os import path
from fmc_hdr import FmcHdr
from prebuilt import PrebuiltType
from prebuilt import PREBUILT_DIR
from prebuilt import PREBUILT_BIN
from typing import List

class FmcInfo:
    pass

class PrebuiltInfo:
    pass

def gen_fmc_info(fmc_path) -> FmcInfo:
    fmc_info = FmcInfo()

    if not path.isfile(fmc_path):
        raise RuntimeError("cannot find FMC binary {}".format(fmc_path))

    f = open(fmc_path, "rb")

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", metavar="IN", help="input FMC raw binary", required=True)
    parser.add_argument("--output", metavar="OUT", help="output FMC binary with header", required=True)
    parser.add_argument("--version", metavar="VER", help="FMC security version number, Default=0", default=0)
    parser.add_argument("--ecc-key", metavar="KEY", help="ECDSA384 signing key (.pem)")
    parser.add_argument("--ecc-key-index", metavar="IDX", help="ECDSA384 signing key index hint, Default=0", default=0)
    parser.add_argument("--lms-key", metavar="KEY", help="LMS signing key (.prv)")
    parser.add_argument("--lms-key-index", metavar="IDX", help="LMS signing key index hint, Default=0", default=0)
    parser.add_argument("--verbose", help="show detail information", action="store_true", default=False)
    args = parser.parse_args()

    fmc_info = gen_fmc_info(args.input)
    pbs_info = gen_prebuilt_info(PREBUILT_DIR, PREBUILT_BIN)

    hdr = FmcHdr()

    hdr.set_fmc_size(fmc_info.size)
    hdr.set_fmc_digest(fmc_info.dgst)

    for pbi in pbs_info:
        hdr.add_prebuilt(pbi.type, pbi.size, pbi.dgst)

    if args.ecc_key is not None:
        pem_f = open(args.ecc_key, "rb")
        pem_d = pem_f.read()

        key = load_pem_private_key(pem_d, password=None)
        sig = key.sign(hdr.output_body(), ec.ECDSA(hashes.SHA384()))
        sig_r, sig_s = decode_dss_signature(sig)

        # convert to bytearray
        sig_r = sig_r.to_bytes(48, byteorder='big')
        sig_s = sig_s.to_bytes(48, byteorder='big')

        hdr.set_ecc_key_index(args.ecc_key_index)
        hdr.set_ecc_signature(sig_r, sig_s)

    # generate final output: Header || FMC Binary || Prebuilt Binaries
    f = open(args.output, "wb")

    f.write(hdr.output(args.verbose))
    f.write(fmc_info.data)
    for pbi in pbs_info:
        f.write(pbi.data)

    f.close()

if __name__ == "__main__":
    main()
