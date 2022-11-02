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

## Usage:

```$ yeat {config} {read1} {read2} --outdir {path} --sample {name}```
