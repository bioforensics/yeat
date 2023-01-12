# YEAT

YEAT, **Y**our **E**verday **A**ssembly **T**ool, is an update to [`asm_tools`](https://github.com/bioforensics/asm_tools). It uses a Snakemake workflow to preprocess, downsample, and assemble paired-end fastq files with various assemblers such as SPAdes, MEGAHIT, and Unicycler.

## Installation

```
git clone https://github.com/bioforensics/yeat.git
cd yeat
conda env create --name yeat --file environment.yml
conda activate yeat
pip install .
```

In order to run [`Bandage`](https://github.com/rrwick/Bandage) in YEAT's workflow, users will need to manually download the pre-built binaries files [here](https://rrwick.github.io/Bandage/) or build it from the source code [here](https://github.com/rrwick/Bandage). Instructions for building Bandage from the source code can be found [here](https://github.com/rrwick/Bandage#building-from-source).

If the pre-built binary files are used, users will need to update their environment's `$PATH` to include the path of the directory containing the binary file.

Example for Ubuntu:
```
export PATH=~/Bandage_Ubuntu_dynamic_v0_8_1:$PATH
```

Example for MacOS:
```
export PATH=~/Bandage_Mac_v0_8_1/Bandage.app/Contents/MacOS:$PATH
```

In order to run the pre-built binary files successfully, ensure that the binary file is kept in the same directory with all of the other files that came with it.

## Usage:

```$ yeat {config} {read1} {read2} --outdir {path} --sample {name}```
