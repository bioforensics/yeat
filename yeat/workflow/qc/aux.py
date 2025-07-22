# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import json
import pandas as pd
import subprocess


def copy_input(input, output, do_copy):
    if do_copy:
        subprocess.run(["cp", input, output])
        return
    subprocess.run(["ln", "-sf", input, output])


def get_genome_size(genome_size, mash_report):
    if genome_size == 0:
        df = pd.read_csv(mash_report, sep="\t")
        return df["Length"].iloc[0]
    return genome_size


def get_average_read_length(fastp_report):
    with open(fastp_report, "r") as fh:
        qcdata = json.load(fh)
    base_count = qcdata["summary"]["after_filtering"]["total_bases"]
    read_count = qcdata["summary"]["after_filtering"]["total_reads"]
    return base_count / read_count


def get_down(downsample, genome_size, coverage_depth, average_read_length):
    if downsample == 0:
        return int((genome_size * coverage_depth) / (2 * average_read_length))
    return downsample


def print_downsample_values(genome_size, average_read_length, coverage_depth, down, seed):
    print(f"[yeat] genome size: {genome_size}")
    print(f"[yeat] average read length: {average_read_length}")
    print(f"[yeat] target depth of coverage: {coverage_depth}x")
    print(f"[yeat] number of reads to sample: {down}")
    print(f"[yeat] random seed for sampling: {seed}")
