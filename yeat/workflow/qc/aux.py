import json
import pandas as pd
from random import randint


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


def get_down(downsample, genome_size, coverage_depth, avg_read_length):
    if downsample == 0:
        return int((genome_size * coverage_depth) / (2 * avg_read_length))
    return downsample


def get_seed(seed):
    if seed == "None":
        return randint(1, 2**16 - 1)
    return seed
