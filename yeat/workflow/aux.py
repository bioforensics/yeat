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
from yeat.config import PACBIO_READS, OXFORD_READS


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
        outread = f"{outdir}/{direction}_reads{i}.fq"
        if inread.endswith(".gz"):
            subprocess.run(f"gunzip -c {inread} > {outread}", shell=True)
        else:
            shutil.copyfile(inread, outread)
    commands = (
        f"cat {outdir}/{direction}_reads*.fq > {outdir}/{direction}_combined-reads.fq;"
        f"gzip {outdir}/{direction}_combined-reads.fq"
    )
    subprocess.run(commands, shell=True)


def get_genome_size(genome_size, mash_report):
    if genome_size == 0:
        df = pd.read_csv(mash_report, sep="\t")
        return df["Length"].iloc[0]
    return genome_size


def get_avg_read_length(fastp_report):
    with open(fastp_report, "r") as fh:
        qcdata = json.load(fh)
    base_count = qcdata["summary"]["after_filtering"]["total_bases"]
    read_count = qcdata["summary"]["after_filtering"]["total_reads"]
    return base_count / read_count


def get_down(downsample, genome_size, coverage, avg_read_length):
    if downsample == 0:
        return int((genome_size * coverage) / (2 * avg_read_length))
    return downsample


def get_seed(seed):
    if seed == "None":
        return randint(1, 2**16 - 1)
    return seed


def print_downsample_values(genome_size, avg_read_length, coverage, down, seed):
    print(f"[yeat] genome size: {genome_size}")
    print(f"[yeat] average read length: {avg_read_length}")
    print(f"[yeat] target depth of coverage: {coverage}x")
    print(f"[yeat] number of reads to sample: {down}")
    print(f"[yeat] random seed for sampling: {seed}")


def get_longread_file(sample, long_readtype):
    if long_readtype in PACBIO_READS:
        return f"seq/input/{sample}/{long_readtype}/combined-reads.fq.gz"
    elif long_readtype in OXFORD_READS:
        return f"seq/nanofilt/{sample}/{long_readtype}/highQuality-reads.fq.gz"
    else:  # pragma: no cover
        message = f"Invalid long readtype '{long_readtype}'"
        raise ValueError(message)
