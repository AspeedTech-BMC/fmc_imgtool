# Copyright (c) 2024 ASPEED Technology Inc.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from hdr_meta import *
from prebuilt import PrebuiltType
import struct

HDR_PREAMBLE_SIZE = 0x8                         # 8
HDR_BODY_SIZE = 0x78                            # 120
HDR_SIZE = HDR_PREAMBLE_SIZE + HDR_BODY_SIZE    # 128
HDR_MAX_FMCSZ = 0x16000                         # 88KB

class FmcHdrV1(FmcHdrMeta):
    def __init__(self):
        super().__init__()

        # Preamble fields
        self.version = 1

        # Body fields
        self.__size = 0
        self.__prebuilt = []

    def set_fmc_size(self, sz: int):
        if sz < 0 or sz > HDR_MAX_FMCSZ:
            raise RuntimeError("invalid image size={}, maximum {}".format(sz, HDR_MAX_FMCSZ))

        self.__size = sz

    def add_prebuilt(self, pb_type: int, pb_size: int):
        if not (pb_type in iter(PrebuiltType)):
            raise RuntimeError("invalid prebuilt binary type={}".format(pb_type))

        if pb_size < 0:
            raise RuntimeError("invalid prebuilt binary size={}".format(pb_size))

        # (type, size)
        self.__prebuilt.append((pb_type, pb_size))

    def output_preamble(self, verbose : bool = False):
        preamble = bytearray(HDR_PREAMBLE_SIZE)

        # print preamble if needed
        if verbose:
            print("--------------")
            print("PREAMBLE")
            print("--------------")
            print("MAGIC                    : {}".format(hex(self.magic)))
            print("VERSION                  : {}".format(hex(self.version)))

        tmp = struct.pack("<2L", self.magic, self.version)

        tmp_len = len(tmp)
        if tmp_len > HDR_PREAMBLE_SIZE:
            raise RuntimeError("invalid preamble size={}, expected <= {}".format(tmp_len, HDR_PREAMBLE_SIZE))

        preamble[: len(tmp)] = tmp

        return preamble

    def output_body(self, verbose : bool = False):
        body = bytearray(HDR_BODY_SIZE)
        tmp = bytearray()

        tmp = struct.pack("<L", self.__size)

        if verbose:
            print("--------------")
            print("BODY")
            print("--------------")
            print("FMC SIZE                 : {}".format(hex(self.__size)))

        ofst = HDR_SIZE + self.__size
        for pb in self.__prebuilt:
            # (type, size)
            tmp += struct.pack("<2L", pb[0], pb[1])

            if verbose:
                print("Prebuilt Type            : {}".format(hex(pb[0])))
                print("Prebuilt Offset          : {}".format(hex(ofst)))
                print("Prebuilt Size            : {}".format(hex(pb[1])))

            ofst += pb[1]

        tmp_len = len(tmp)
        if tmp_len > HDR_BODY_SIZE:
            raise RuntimeError("invalid body size={}, expected <= {}".format(tmp_len, HDR_BODY_SIZE))

        body[: tmp_len] = tmp

        return body

    def output(self, verbose : bool = False):
        preamble = self.output_preamble(verbose)
        body = self.output_body(verbose)

        return preamble + body
