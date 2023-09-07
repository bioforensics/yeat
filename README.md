# YEAT

YEAT, **Y**our **E**verday **A**ssembly **T**ool, is an update to [`asm_tools`](https://github.com/bioforensics/asm_tools). It uses a Snakemake workflow to preprocess paired-end, pacbio, and nanopore fastq reads and assemble them with various assembly algorithms.

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
export PATH=~/projects/Bandage:$PATH
```

Example for MacOS:
```
export PATH=~/projects/Bandage/Bandage.app/Contents/MacOS:$PATH
```

In order to run the pre-built binary files successfully, ensure that the binary file is kept in the same directory with all of the other files that came with it.


### Installing metaMDBG (for Linux OS only)

To enable `metaMDBG` into YEAT's workflow, users will need to create a conda environment, install, and build from the source. Once created, YEAT will activate the environment whenever `metaMDBG` is called.

#### Download metaMDBG repository  
```
git clone https://github.com/GaetanBenoitDev/metaMDBG.git
```

#### Create metaMDBG conda environment
```
cd metaMDBG
conda env create -f conda_env.yml
conda activate metaMDBG
conda env config vars set CPATH=${CONDA_PREFIX}/include:${CPATH}
conda deactivate

# Activate metaMDBG environment
conda activate metaMDBG

# Compile the software
mkdir build
cd build
cmake ..
make -j 3
```

After successful installation, an executable named metaMDBG will appear in ./build/bin.

#### Link the binary to the environment's bin
```
ln -s ~/projects/metaMDBG/build/bin/metaMDBG /home/danejo/anaconda3/envs/metaMDBG/bin/metaMDBG
```

### Running PacBio Hifi and Nanopore-Reads Tests For Developers

Before running the test suite, download the test data by calling the following make commands.

```
make hifidata
make nanodata
make metadata
```

## Usage:

```
$ yeat --outdir {path} {config}
```

### Supported Input Reads with Assembly Algorithms

| Readtype  | Algorithm |
| ------------- | ------------- |
| paired  | spades, megahit, unicycler |
| single  | spades, megahit, unicycler |
| pacbio-raw  | flye, canu |
| pacbio-corr  | flye, canu |
| pacbio-hifi  | flye, canu, hifiasm, hifiasm-meta, metamdbg* |
| nano-raw  | flye, canu |
| nano-corr  | flye, canu |
| nano-hq  | flye, canu |

\* \- available on Linux OS only


### Example config file

```
{
    "samples": {
        "sample1": {
            "paired": [
                "yeat/tests/data/short_reads_1.fastq.gz",
                "yeat/tests/data/short_reads_2.fastq.gz"
            ]
        },
        "sample2": {
            "paired": [
                "yeat/tests/data/Animal_289_R1.fq.gz",
                "yeat/tests/data/Animal_289_R2.fq.gz"
            ]
        },
        "sample3": {
            "pacbio-hifi": [
                "yeat/tests/data/ecoli.fastq.gz"
            ]
        },
        "sample4": {
            "nano-hq": [
                "yeat/tests/data/ecolk12mg1655_R10_3_guppy_345_HAC.fastq.gz"
            ]
        }
    },
    "assemblers": [
        {
            "label": "spades-default",
            "algorithm": "spades",
            "extra_args": "",
            "samples": [
                "sample1",
                "sample2"
            ]
        },
        {
            "label": "hicanu",
            "algorithm": "canu",
            "extra_args": "genomeSize=4.8m",
            "samples": [
                "sample3"
            ]
        },
        {
            "label": "flye_ONT",
            "algorithm": "flye",
            "extra_args": "",
            "samples": [
                "sample4"
            ]
        }
    ]
}
```
