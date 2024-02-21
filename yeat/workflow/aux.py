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
import warnings


def get_and_filter_contig_files(sample, readtype, label):
    pattern = rf"analysis/{sample}/{readtype}/{label}/megahit/intermediate_contigs/k\d+.contigs.fa"
    contigs = glob.glob(
        rf"analysis/{sample}/{readtype}/{label}/megahit/intermediate_contigs/k*.contigs.fa"
    )
    return filter(re.compile(pattern).match, contigs)


def get_canu_readtype_flag(readtype):
    if readtype in ["pacbio-raw", "pacbio-corr"]:
        return "-pacbio"
    elif readtype == "pacbio-hifi":  # pragma: no cover
        return "-pacbio-hifi"


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


def get_expected_files(config):
    run_bandage = check_bandage()
    inputlist = []
    for assembly_label, assembly_obj in config["assemblies"].items():
        for sample_label in assembly_obj.samples:
            sample_obj = config["samples"][sample_label]
            if assembly_obj.mode in ["paired", "single"]:
                inputlist.append(
                    get_file(
                        run_bandage,
                        sample_label,
                        sample_obj.short_readtype,
                        assembly_label,
                        assembly_obj.algorithm,
                    )
                )
            elif assembly_obj.mode in ["pacbio", "oxford"]:
                inputlist.append(
                    get_file(
                        run_bandage,
                        sample_label,
                        sample_obj.long_readtype,
                        assembly_label,
                        assembly_obj.algorithm,
                    )
                )
            elif assembly_obj.mode == "hybrid":  # pragma: no cover
                inputlist.append(
                    get_file(
                        run_bandage, sample_label, "hybrid", assembly_label, assembly_obj.algorithm
                    )
                )
            if assembly_obj.mode in ["paired", "hybrid"]:
                inputlist += [
                    f"seq/fastqc/{sample_label}/paired/{direction}_combined-reads_fastqc.html"
                    for direction in ["r1", "r2"]
                ]
            if assembly_obj.mode == "single":
                inputlist.append(f"seq/fastqc/{sample_label}/single/combined-reads_fastqc.html")
            if assembly_obj.mode in ["pacbio", "hybrid"]:
                inputlist.append(
                    f"seq/fastqc/{sample_label}/{sample_obj.long_readtype}/combined-reads_fastqc.html"
                )
            if assembly_obj.mode == ["oxford", "hybrid"]:
                inputlist += [
                    f"seq/nanoplot/{sample_label}/{sample_obj.long_readtype}/{quality}_LengthvsQualityScatterPlot_dot.pdf"
                    for quality in ["raw", "filtered"]
                ]
    return inputlist


def check_bandage():
    try:
        completed_process = subprocess.run(["Bandage", "--help"], capture_output=True, text=True)
    except Exception as exception:
        print(f"{type(exception).__name__}: {exception}")
        warnings.warn("Unable to run Bandage; skipping Bandage")
        return False
    if completed_process.returncode == 1:
        print(completed_process.stderr)
        warnings.warn("Unable to run Bandage; skipping Bandage")
        return False
    return True


def get_file(run_bandage, sample, readtype, assembly, algorithm):
    if run_bandage:
        return f"analysis/{sample}/{readtype}/{assembly}/{algorithm}/bandage/.done"
    return f"analysis/{sample}/{readtype}/{assembly}/{algorithm}/quast/report.html"


def get_longread(sample, long_readtype):
    if long_readtype in ["nano-raw", "nano-corr", "nano-hq"]:
        return f"seq/nanofilt/{sample}/{long_readtype}/highQuality-reads.fq.gz"
    if long_readtype in ["pacbio-raw", "pacbio-corr", "pacbio-hifi"]:
        return f"seq/input/{sample}/{long_readtype}/combined-reads.fq.gz"
    assert 0  # should never get here
