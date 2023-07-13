# YEAT

YEAT, **Y**our **E**verday **A**ssembly **T**ool, is an update to [`asm_tools`](https://github.com/bioforensics/asm_tools). It uses a Snakemake workflow to preprocess paired-end, pacbio, and nanopore fastq reads and assemble them with various assembly algorithms such as SPAdes, MEGAHIT, Unicycler, Canu, and Flye.

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

### Running PacBio Hifi and Nanopore-Reads Tests For Developers

Before running the test suite, download the filtered 25x coverage E. coli Hifi-read and Escherichia coli K12 nanopore data by calling the following make command.

```
make hifidata
make nanodata
```

## Usage:

```
$ yeat --outdir {path} {config}
```

### Supported Input Reads with Assembler Algorithms

| Readtype  | Algorithm |
| ------------- | ------------- |
| paired  | Spades, Megahit, Unicycler |
| pacbio-raw  | Flye, Canu |
| pacbio-corr  | Flye, Canu |
| pacbio-hifi  | Flye, Canu |
| nano-raw  | Flye, Canu |
| nano-corr  | Flye, Canu |
| nano-hq  | Flye, Canu |


### Example config file

```
{
    "samples": {
        "sample1": {
            "paired": [
                "/Users/dane.jo/Desktop/test1/data/short1.fq.gz",
                "/Users/dane.jo/Desktop/test1/data/short2.fq.gz"
            ]
        },
        "sample2": {
            "paired": [
                "/Users/dane.jo/Desktop/test1/data/Animal_289_R1.fq.gz",
                "/Users/dane.jo/Desktop/test1/data/Animal_289_R2.fq.gz"
            ]
        },
        "sample3": {
            "pacbio-hifi": [
                "/Users/dane.jo/Desktop/test1/data/ecoli.fastq.gz"
            ]
        },
        "sample4": {
            "nano-hq": [
                "/Users/dane.jo/Desktop/test1/data/ecolk12mg1655_R10_3_guppy_345_HAC.fastq.gz"
            ]
        }
    },
    "assemblers": [
        {
            "label": "spades-meta",
            "algorithm": "spades",
            "extra_args": "--meta",
            "samples": [
                "sample1",
                "sample2"
            ]
        },
	    {
            "label": "hicanu",
            "algorithm": "canu",
            "extra_args": "genomeSize=4.6m",
            "samples": [
                "sample3"
            ]
        },
        {
            "label": "hiflye",
            "algorithm": "flye",
            "extra_args": "",
            "samples": [
                "sample3"
            ]
        },
        {
            "label": "nanoflye",
            "algorithm": "flye",
            "extra_args": "",
            "samples": [
                "sample4"
            ]
        }
    ]
}
```
