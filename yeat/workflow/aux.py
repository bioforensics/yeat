# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import glob
import json
import pandas as pd
from random import randint
import re
import shutil
import subprocess

# from yeat.config import PACBIO_READS, OXFORD_READS


# from yeat.assemblers.assembler import Assembly
# from yeat.config.config import Config
# from yeat.config.sample import Sample


# def create_config(config):
#     samples = {key: Sample(**value) for key, value in config.get("samples", {}).items()}
#     assemblies = {key: Assembly(**value) for key, value in config.get("assemblies", {}).items()}
#     return Config(samples, assemblies)


def get_and_filter_contig_files(sample, readtype, label):
    pattern = rf"analysis/{sample}/{readtype}/{label}/megahit/intermediate_contigs/k\d+.contigs.fa"
    contigs = glob.glob(
        rf"analysis/{sample}/{readtype}/{label}/megahit/intermediate_contigs/k*.contigs.fa"
    )
    return filter(re.compile(pattern).match, contigs)


def get_canu_readtype_flag(readtype):
    if readtype in ["pacbio-raw", "pacbio-corr"]:
        return "-pacbio"
    elif readtype == "pacbio-hifi":
        return "-pacbio-hifi"
    else:  # pragma: no cover
        message = f"Invalid readtype '{readtype}'"
        raise ValueError()


def combine(reads, direction, outdir):
    for i, inread in enumerate(reads):
        outread = f"{outdir}/{direction}_reads{i}.fq.gz"
        if not inread.endswith(".gz"):
            subprocess.run(f"gzip {inread} > {outread}", shell=True)
        else:
            shutil.copyfile(inread, outread)
    commands = (
        f"cat {outdir}/{direction}_reads*.fq.gz > {outdir}/{direction}_combined-reads.fq.gz;"
        f"rm {outdir}/{direction}_reads*.fq.gz"
    )
    subprocess.run(commands, shell=True)


def print_downsample_values(genome_size, avg_read_length, coverage_depth, down, seed):
    print(f"[yeat] genome size: {genome_size}")
    print(f"[yeat] average read length: {avg_read_length}")
    print(f"[yeat] target depth of coverage: {coverage_depth}x")
    print(f"[yeat] number of reads to sample: {down}")
    print(f"[yeat] random seed for sampling: {seed}")


# def get_longread_file(sample, long_readtype):
#     if long_readtype in PACBIO_READS:
#         return f"seq/input/{sample}/{long_readtype}/combined-reads.fq.gz"
#     elif long_readtype in OXFORD_READS:
#         return f"seq/nanofilt/{sample}/{long_readtype}/highQuality-reads.fq.gz"
#     else:  # pragma: no cover
#         message = f"Invalid long readtype '{long_readtype}'"
#         raise ValueError(message)


from pathlib import Path


def get_slurm_logs_dir(wd):
    return Path(wd).resolve() / "slurm-logs/"


def copy_input(input, output, do_copy):
    if do_copy:
        subprocess.run(["cp", input, output])
    else:
        subprocess.run(["ln", "-sf", input, output])
