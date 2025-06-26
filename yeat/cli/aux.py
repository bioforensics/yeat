# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from argparse import Action, ArgumentTypeError
from pathlib import Path
from yeat.config.assembly import Assembly
from yeat.config.config import Config
from yeat.config.sample import Sample


class InitAction(Action):
    # CONFIG_TEMPLATE = CONFIG(
    #     samples={
    #         "sample1": SAMPLE(illumina=["path/to/data/sample1_R1.fastq.gz", "path/to/data/sample1_R2.fastq.gz"],),
    #         "sample2": SAMPLE(illumina="path/to/data/sample2_single.fastq.gz"),
    #         "sample3": SAMPLE(ont="path/to/data/sample3_ont.fastq.gz"),
    #         "sample4": SAMPLE(pacbio="path/to/data/sample4_hifi.fastq.gz"),
    #     },
    #     assemblies={
    #         "short_paired": ASSEMBLY(algorithm="spades", mode="paired", extra_args=""),
    #         "short_single": ASSEMBLY(algorithm="spades", mode="paired", extra_args=""),
    #         "long_ont": ASSEMBLY(algorithm="flye", mode="ont", extra_args=""),
    #         "long_hifi": ASSEMBLY(algorithm="flye", mode="pacbio", extra_args=""),
    #     },
    # )

    def __call__(self, parser, namespace, values, option_string=None):
        # print(self.CONFIG_TEMPLATE)
        raise SystemExit()


def check_positive(value):
    try:
        value = int(value)
        if value <= 0:
            raise ArgumentTypeError(f"{value} is not a positive integer")
    except ValueError:
        raise ArgumentTypeError(f"{value} is not an integer")
    return value


def get_slurm_logs_dir(wd):
    return Path(wd).resolve() / "slurm-logs/"
