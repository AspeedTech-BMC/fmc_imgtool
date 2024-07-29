from enum import IntEnum
from enum import auto

class PrebuiltType(IntEnum):
    PREBUILT_TYPE_END = 0

    DDR4_PMU_TRAIN_IMEM = auto()
    DDR4_PMU_TRAIN_DMEM = auto()
    DDR4_2D_PMU_TRAIN_IMEM = auto()
    DDR4_2D_PMU_TRAIN_DMEM = auto()
    DDR5_PMU_TRAIN_IMEM = auto()
    DDR5_PMU_TRAIN_DMEM = auto()
    DP_FW = auto()
    UEFI_X64_AST2700 = auto()

PREBUILT_DIR = "prebuilt/"
PREBUILT_BIN = {
    "ddr4_pmu_train_imem.bin"       : PrebuiltType.DDR4_PMU_TRAIN_IMEM,
    "ddr4_pmu_train_dmem.bin"       : PrebuiltType.DDR4_PMU_TRAIN_DMEM,
    "ddr4_2d_pmu_train_imem.bin"    : PrebuiltType.DDR4_2D_PMU_TRAIN_IMEM,
    "ddr4_2d_pmu_train_dmem.bin"    : PrebuiltType.DDR4_2D_PMU_TRAIN_DMEM,
    "ddr5_pmu_train_imem.bin"       : PrebuiltType.DDR5_PMU_TRAIN_IMEM,
    "ddr5_pmu_train_dmem.bin"       : PrebuiltType.DDR5_PMU_TRAIN_DMEM,
    "dp_fw.bin"                     : PrebuiltType.DP_FW,
    "uefi_x64_ast2700.bin"          : PrebuiltType.UEFI_X64_AST2700,
}
