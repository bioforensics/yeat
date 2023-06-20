# YEAT

YEAT, **Y**our **E**verday **A**ssembly **T**ool, is an update to [`asm_tools`](https://github.com/bioforensics/asm_tools). It uses a Snakemake workflow to preprocess paired-end and pacbio-hifi fastq reads with various assemblers such as SPAdes, MEGAHIT, Unicycler, Canu, and Flye.

## Installation

```
git clone https://github.com/bioforensics/yeat.git
cd yeat
conda env create --name yeat --file environment.yml
conda activate yeat
pip install .
```

### Bandage

In order to run [`Bandage`](https://github.com/rrwick/Bandage) in YEAT's workflow, users will need to manually download the pre-built binaries files [here](https://rrwick.github.io/Bandage/) or build it from the source code [here](https://github.com/rrwick/Bandage). Instructions for building Bandage from the source code can be found [here](https://github.com/rrwick/Bandage#building-from-source).

Once the binary file has been obtained, users will need to update their environment's `$PATH` to include the path to the directory containing the binary file.

Example for Ubuntu:
```
export PATH={BANDAGE_DIR}:$PATH
```

Example for MacOS:
```
export PATH={BANDAGE_DIR}/Bandage.app/Contents/MacOS:$PATH
```

In order to run the pre-built binary files successfully, ensure that the binary file is kept in the same directory with all of the other files that came with it.

### Running PacBio Hifi-Reads Tests For Developers

Before running the test suite, download the filtered 25x coverage E. coli Hifi-read data by calling the following make command.

```
make hifidata
```

## Usage:

```
$ yeat --outdir {path} {config}
```
