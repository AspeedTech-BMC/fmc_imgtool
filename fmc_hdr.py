from prebuilt import PrebuiltType
import struct

ECC_KEY_LEN = 96            # ECDSA384
LMS_KEY_LEN = 1620          # LMS_SHA256_N24_H15 + LMOTS_SHA256_N24_W4
SHA_DGST_LEN = 48           # SHA384

HDR_MAGIC = 0x48545341                          # ASTH
HDR_PREAMBLE_SIZE = 0x700                       # 1792
HDR_BODY_SIZE = 0x300                           # 768
HDR_SIZE = HDR_PREAMBLE_SIZE + HDR_BODY_SIZE    # 2560
HDR_MAX_SVN = 64                                # correspond to 64-bits bitmap in OTP
HDR_MAX_KEYID = 16                              # correspond to 16-bits bitmap in OTP
HDR_MAX_FMCSZ = 0x38000                         # 224KB

class FmcHdr:
    def __init__(self):
        # Preamble fields
        self.__magic = HDR_MAGIC
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
            raise RuntimeError("invalid image size={}, maximum {}".format(sz, HDR_MAX_IMGSZ))

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

        self.__prebuilt.append((pb_type, pb_size, pb_dgst[: SHA_DGST_LEN]))

    def output(self):
        preamble = bytearray(HDR_PREAMBLE_SIZE)
        body = bytearray(HDR_BODY_SIZE)

        tmp = struct.pack("<L2H", self.__magic, self.__ecc_key_index, self.__lms_key_index)
        tmp += self.__ecc_signature
        tmp += self.__lms_signature

        preamble[: len(tmp)] = tmp

        tmp = struct.pack("<L", self.__size)[:3]
        tmp += struct.pack("B", self.__svn)
        tmp += self.__sha384_dgst

        for pb in self.__prebuilt:
            tmp += struct.pack("<L", pb[1])[:3]
            tmp += struct.pack("B", pb[0])
            tmp += pb[2]

        body[: len(tmp)] = tmp

        return preamble + body
