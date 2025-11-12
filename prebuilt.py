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
    UEFI_AST2700 = auto()

PREBUILT_BIN = {
    "ddr4_pmu_train_imem.bin"       : PrebuiltType.DDR4_PMU_TRAIN_IMEM,
    "ddr4_pmu_train_dmem.bin"       : PrebuiltType.DDR4_PMU_TRAIN_DMEM,
    "ddr4_2d_pmu_train_imem.bin"    : PrebuiltType.DDR4_2D_PMU_TRAIN_IMEM,
    "ddr4_2d_pmu_train_dmem.bin"    : PrebuiltType.DDR4_2D_PMU_TRAIN_DMEM,
    "ddr5_pmu_train_imem.bin"       : PrebuiltType.DDR5_PMU_TRAIN_IMEM,
    "ddr5_pmu_train_dmem.bin"       : PrebuiltType.DDR5_PMU_TRAIN_DMEM,
    "dp_fw.bin"                     : PrebuiltType.DP_FW,
    "uefi_ast2700.bin"          : PrebuiltType.UEFI_AST2700,
}
