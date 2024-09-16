from hdr_meta import *
from prebuilt import PrebuiltType
import struct

ECC_KEY_LEN = 96            # ECDSA384
LMS_KEY_LEN = 1620          # LMS_SHA256_N24_H15 + LMOTS_SHA256_N24_W4
SHA_DGST_LEN = 48           # SHA384

HDR_PREAMBLE_SIZE = 0x700                       # 1792
HDR_BODY_SIZE = 0x300                           # 768
HDR_SIZE = HDR_PREAMBLE_SIZE + HDR_BODY_SIZE    # 2560
HDR_MAX_SVN = 64                                # correspond to 64-bits bitmap in OTP
HDR_MAX_KEYID = 16                              # correspond to 16-bits bitmap in OTP
HDR_MAX_FMCSZ = 0x38000                         # 224KB

class FmcHdrV2(FmcHdrMeta):
    def __init__(self):
        super().__init__()

        # Preamble fields
        self.version = 2
        self.__ecc_key_index = 0
        self.__lms_key_index = 0
        self.__ecc_signature = bytearray(ECC_KEY_LEN)
        self.__lms_signature = bytearray(LMS_KEY_LEN)

        # Body fields
        self.__size = 0
        self.__svn = 0
        self.__sha384_dgst = bytearray(SHA_DGST_LEN)
        self.__prebuilt = []

    # Preamble field accessor
    def set_ecc_key_index(self, i: int):
        if i < 0 or i >= HDR_MAX_KEYID:
            raise RuntimeError("invalid ECC key index, expected 0 ~ 15")

        self.__ecc_key_index = i

    def set_ecc_signature(self, r: bytearray, s: bytearray):
        r_len = ECC_KEY_LEN // 2
        s_len = ECC_KEY_LEN // 2

        if len(r) != r_len:
            raise RuntimeError("invalid ECDSA384 'r' length={}, expected {}".format(len(r), r_len))

        if len(s) != s_len:
            raise RuntimeError("invalid ECDSA384 's' length={}, expected {}".format(len(s), s_len))

        self.__ecc_signature[: r_len] = r
        self.__ecc_signature[r_len :] = s

    def set_lms_key_index(self, i: int):
        if i < 0 or i > HDR_MAX_KEYID:
            raise RuntimeError("invalid LMS key index")

        self.__lms_key_index = i

    def set_lms_signature(self, s: bytearray):
        if len(s) < LMS_KEY_LEN:
            raise RuntimeError("invalid LMS N24/H15/W4 length={}, expected {}".format(len(s), LMS_KEY_LEN))

        self.__lms_signature[: LMS_KEY_LEN] = s

    # Body field accessor
    def set_fmc_svn(self, v: int):
        if v < 0 or v > HDR_MAX_SVN:
            raise RuntimeError("invalid SVN={}, maximum {}".format(v, HDR_MAX_SVN))

        self.__svn = v

    def set_fmc_size(self, sz: int):
        if sz < 0 or sz > HDR_MAX_FMCSZ:
            raise RuntimeError("invalid image size={}, maximum {}".format(sz, HDR_MAX_FMCSZ))

        self.__size = sz

    def set_fmc_digest(self, dgst: bytearray):
        if len(dgst) < SHA_DGST_LEN:
            raise RuntimeError("invalid SHA384 digest length={}, expected {}".format(len(dgst), SHA_DGST_LEN))

        self.__sha384_dgst[: SHA_DGST_LEN] = dgst

    def add_prebuilt(self, pb_type: int, pb_size: int, pb_dgst: bytearray):
        if not (pb_type in iter(PrebuiltType)):
            raise RuntimeError("invalid prebuilt binary type={}".format(pb_type))

        if pb_size < 0:
            raise RuntimeError("invalid prebuilt binary size={}".format(pb_size))

        if len(pb_dgst) < SHA_DGST_LEN:
            raise RuntimeError("invalid prebuilt binary digest length={}".format(len(pb_dgst)))

        # (type, size, dgst)
        self.__prebuilt.append((pb_type, pb_size, pb_dgst[: SHA_DGST_LEN]))

    def output_preamble(self, verbose: bool = False):
        preamble = bytearray(HDR_PREAMBLE_SIZE)

        # print preamble if needed
        if verbose:
            print("--------------")
            print("PREAMBLE")
            print("--------------")
            print("MAGIC                    : {}".format(hex(self.magic)))
            print("VERSION                  : {}".format(hex(self.version)))
            print("ECC_KEY_INDEX            : {}".format(hex(self.__ecc_key_index)))
            print("LMS_KEY_INDEX            : {}".format(hex(self.__lms_key_index)))
            print("ECC_SIGNATURE (32 MSByte): {}".format(self.__ecc_signature.hex()[: 64]))
            print("LMS_SIGNATURE (32 MSByte): {}".format(self.__lms_signature.hex()[: 64]))

        tmp = struct.pack("<4L", self.magic, self.version, self.__ecc_key_index, self.__lms_key_index)
        tmp += self.__ecc_signature
        tmp += self.__lms_signature

        tmp_len = len(tmp)
        if tmp_len > HDR_PREAMBLE_SIZE:
            raise RuntimeError("invalid preamble size={}, expected <= {}".format(tmp_len, HDR_PREAMBLE_SIZE))

        preamble[: tmp_len] = tmp

        return preamble

    def output_body(self, verbose : bool = False):
        body = bytearray(HDR_BODY_SIZE)

        tmp = struct.pack("<2L", self.__svn, self.__size)
        tmp += self.__sha384_dgst

        if verbose:
            print("--------------")
            print("BODY")
            print("--------------")
            print("FMC SIZE                 : {}".format(hex(self.__size)))
            print("FMC SVN                  : {}".format(hex(self.__svn)))
            print("FMC DIGEST               : {}".format(self.__sha384_dgst.hex()))

        ofst = HDR_SIZE + self.__size
        for pb in self.__prebuilt:
            # (type, size, dgst)
            tmp += struct.pack("<2L", pb[0], pb[1])
            tmp += pb[2]

            if verbose:
                print("Prebuilt Type            : {}".format(hex(pb[0])))
                print("Prebuilt Offset          : {}".format(hex(ofst)))
                print("Prebuilt Size            : {}".format(hex(pb[1])))
                print("Prebuilt Digest          : {}".format(pb[2].hex()))

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
