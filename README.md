# ASPEED FMC_IMGTOOL

ASPEED FMC image tool is to pack the SoC FMC image with the header for runtime FW load, including FW itself and the prebuilt binaries in AST27xx series.

# Requirement

- python v3.7.0 and above

# Usage

#### Setting Up

```bash
git clone https://github.com/AspeedTech-BMC/fmc_imgtool.git
cd fmc_imgtool/
python -m venv venv
. venv/bin/activate
pip install build
python -m build
pip install dist/fmc_imgtool-0.1.2-py3-none-any.whl  --force-reinstall
```

```bash
usage: fmc-imgtool [-h] --input IN --output OUT --version {1,2} [--svn SVN] [--ecc-key KEY] [--ecc-key-index IDX] [--lms-key KEY] [--lms-key-index IDX] [--prebuilt-dir DIR] [--verbose]

options:
  -h, --help           show this help message and exit
  --input IN           input FMC raw binary
  --output OUT         output FMC binary with header
  --version {1,2}      FMC header version
  --svn SVN            FMC security version number, Default=0
  --ecc-key KEY        ECDSA384 signing key (.pem)
  --ecc-key-index IDX  ECDSA384 signing key index hint, Default=0
  --lms-key KEY        LMS signing key (.prv)
  --lms-key-index IDX  LMS signing key index hint, Default=0
  --prebuilt-dir DIR   prebuilt binaries directory, Default=prebuilt/
  --verbose            show detail information
```

## FMC Header Format - v1

- This header format is used in AST2700-A0 to load the prebuilt binaries.
![Header Format v1](images/hdr_format_v1.png)

## FMC Header Format - v2

- This header format is used in AST2700-A1 ROM for secure boot and FMC for loading and verifying the prebuilt binaries.
![Header Format v2](images/hdr_format_v2.png)

### Command Usage

- FMC + Header
```bash
$ python3 main.py --version 2 --prebuilt bmc-pb/ast2700a1/ --input fmc_raw.bin --output fmc.bin
```

- FMC + Header + ECC Signature
```bash
$ python3 main.py --version 2 --prebuilt bmc-pb/ast2700a1/ --input fmc_raw.bin --output fmc.bin --ecc-key pri.pem --ecc-key-index 0
```

- FMC + Header + ECC Signature + LMS Signature
```bash
$ python3 main.py --version 2 --prebuilt bmc-pb/ast2700a1/ --input fmc_raw.bin --output fmc.bin --ecc-key pri.pem --ecc-key-index 0 --lms-key lms_key.prv --lms-key-index 0​
```