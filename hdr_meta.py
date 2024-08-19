import abc

HDR_MAGIC = 0x48545341  # ASTH

class FmcHdrMeta(metaclass=abc.ABCMeta):

    def __init__(self):
        # common fields across all versions of FMC header
        self.magic = HDR_MAGIC
        self.version = 0xffffffff

    @abc.abstractmethod
    def output_preamble(self, verbose: bool = False):
        return NotImplemented

    @abc.abstractmethod
    def output_body(self, verbose : bool = False):
        return NotImplemented

    @abc.abstractmethod
    def output(self, verbose : bool = False):
        return NotImplemented
