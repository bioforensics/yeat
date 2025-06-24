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
from yeat.config.assembly import ASSEMBLY
from yeat.config.config import CONFIG
from yeat.config.sample import SAMPLE


CONFIG_TEMPLATE = CONFIG(
    samples={
        "sample1": SAMPLE(
            reads=["path/to/data/sample1-R1.fastq.gz", "path/to/data/sample1-R1.fastq.gz"],
            platform="illumina",
        ),
        "sample2": SAMPLE(reads=["path/to/data/sample2_ont.fastq.gz"], platform="ont"),
        "sample3": SAMPLE(reads=["path/to/data/sample3_hifi.fastq.gz"], platform="pacbio"),
    },
    assemblies={
        "assembly1": ASSEMBLY(algorithm="spades", mode="paired", extra_args=""),
        "assembly2": ASSEMBLY(algorithm="flye", mode="ont", extra_args=""),
        "assembly3": ASSEMBLY(algorithm="flye", mode="pacbio", extra_args=""),
    },
)


class InitAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(CONFIG_TEMPLATE)
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
