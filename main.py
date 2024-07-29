#!/usr/bin/env python3

import argparse
import hashlib
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

def gen_fmc_signature():
    print("todo")

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
    parser.add_argument("--version", metavar="VER", help="Security version number", default=0)
    parser.add_argument("--ecc-key", metavar="KEY", help="ECDSA384 signing key")
    parser.add_argument("--ecc-key-index", metavar="IDX", help="ECDSA384 signing key index hint", default=0)
    parser.add_argument("--lms-key", metavar="KEY", help="LMS signing key")
    parser.add_argument("--lms-key-index", metavar="IDX", help="LMS signing key index hint", default=0)
    parser.add_argument("--verbose", help="show detail information", action="store_true", default=False)
    args = parser.parse_args()

    fmc_info = gen_fmc_info(args.input)
    pbs_info = gen_prebuilt_info(PREBUILT_DIR, PREBUILT_BIN)

    if args.verbose:
        print("FMC Size: {}\n"
              "FMC Dgst: {}\n".format(hex(fmc_info.size), fmc_info.dgst.hex()))

        for pbi in pbs_info:
            print("PB Type: {} ({})\n"
                  "PB Name: {}\n"
                  "PB Size: {}\n"
                  "PB Dgst: {}\n".format(pbi.type, PrebuiltType(pbi.type).name, pbi.name, hex(pbi.size), pbi.dgst.hex()))

    hdr = FmcHdr()
    hdr.set_fmc_size(fmc_info.size)
    hdr.set_fmc_digest(fmc_info.dgst)

    for pbi in pbs_info:
        hdr.add_prebuilt(pbi.type, pbi.size, pbi.dgst)

    #
    # TODO: sign FMC header
    #

    # generate final output: Header || FMC Binary || Prebuilt Binaries
    f = open(args.output, "wb")

    f.write(hdr.output())
    f.write(fmc_info.data)
    for pbi in pbs_info:
        f.write(pbi.data)

    f.close()

if __name__ == "__main__":
    main()
