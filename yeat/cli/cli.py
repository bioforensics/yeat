# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import illumina
from argparse import Action, ArgumentParser
import json
from pathlib import Path
import sys
import yeat


CONFIG_TEMPLATE = {
    "samples": {
        "sample1": {
            "paired": [
                [
                    "yeat/tests/data/short_reads_1.fastq.gz",
                    "yeat/tests/data/short_reads_2.fastq.gz",
                ]
            ]
        },
        "sample2": {
            "paired": [
                ["yeat/tests/data/Animal_289_R1.fq.gz", "yeat/tests/data/Animal_289_R2.fq.gz"]
            ]
        },
        "sample3": {"pacbio-hifi": ["yeat/tests/data/ecoli.fastq.gz"]},
        "sample4": {"nano-hq": ["yeat/tests/data/ecolk12mg1655_R10_3_guppy_345_HAC.fastq.gz"]},
    },
    "assemblies": {
        "spades-default": {
            "algorithm": "spades",
            "extra_args": "",
            "samples": ["sample1", "sample2"],
            "mode": "paired",
        },
        "hicanu": {
            "algorithm": "canu",
            "extra_args": "genomeSize=4.8m",
            "samples": ["sample3"],
            "mode": "pacbio",
        },
        "flye_ONT": {
            "algorithm": "flye",
            "extra_args": "",
            "samples": ["sample4"],
            "mode": "oxford",
        },
    },
}


class InitAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        json.dump(CONFIG_TEMPLATE, sys.stdout, indent=4)
        print()
        raise SystemExit()


def get_parser(exit_on_error=True):
    parser = ArgumentParser(add_help=False, exit_on_error=exit_on_error)
    optional_options(parser)
    workflow_options(parser)
    illumina.fastp_options(parser)
    illumina.downsample_options(parser)
    parser.add_argument("config", help="config file", type=lambda p: str(Path(p).resolve()))
    return parser


def optional_options(parser):
    parser.add_argument(
        "--init",
        action=InitAction,
        nargs=0,
        help="print a template assembly config file to the terminal (stdout) and exit",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help="show this help message and exit",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"YEAT v{yeat.__version__}",
    )


def workflow_options(parser):
    workflow = parser.add_argument_group("workflow arguments")
    workflow.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="construct workflow DAG and print a summary but do not execute",
    )
    workflow.add_argument(
        "-o",
        "--outdir",
        default=".",
        help="output directory; default is current working directory",
        metavar="DIR",
        type=str,
    )
    workflow.add_argument(
        "-t",
        "--threads",
        default=1,
        help="execute workflow with T threads; by default, T=1",
        metavar="T",
        type=int,
    )
