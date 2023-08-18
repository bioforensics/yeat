# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import illumina
from .config import AssemblerConfig
from argparse import Action, ArgumentParser
import json
import sys
import yeat
from yeat import workflows


CONFIG_TEMPLATE = {
    "samples": {
        "sample1": {
            "paired": [
                "yeat/tests/data/short_reads_1.fastq.gz",
                "yeat/tests/data/short_reads_2.fastq.gz",
            ]
        },
        "sample2": {
            "paired": [
                "yeat/tests/data/Animal_289_R1.fq.gz",
                "yeat/tests/data/Animal_289_R2.fq.gz",
            ]
        },
        "sample3": {"pacbio-hifi": ["yeat/tests/data/ecoli.fastq.gz"]},
        "sample4": {"nano-hq": ["yeat/tests/data/ecolk12mg1655_R10_3_guppy_345_HAC.fastq.gz"]},
    },
    "assemblers": [
        {
            "label": "spades-default",
            "algorithm": "spades",
            "extra_args": "",
            "samples": ["sample1", "sample2"],
        },
        {
            "label": "hicanu",
            "algorithm": "canu",
            "extra_args": "genomeSize=4.8m",
            "samples": ["sample3"],
        },
        {"label": "flye_ONT", "algorithm": "flye", "extra_args": "", "samples": ["sample4"]},
    ],
}


class InitAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        json.dump(CONFIG_TEMPLATE, sys.stdout, indent=4)
        print()
        raise SystemExit()


def options(parser):
    parser.add_argument("-v", "--version", action="version", version=f"YEAT v{yeat.__version__}")
    parser.add_argument(
        "--init",
        action=InitAction,
        nargs=0,
        help="print a template assembly config file to the terminal (stdout) and exit",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        type=str,
        metavar="DIR",
        default=".",
        help="output directory; default is current working directory",
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        metavar="T",
        default=1,
        help="execute workflow with T threads; by default T=1",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="construct workflow DAG and print a summary but do not execute",
    )


def get_parser(exit_on_error=True):
    parser = ArgumentParser(exit_on_error=exit_on_error)
    options(parser)
    illumina.fastp_options(parser)
    illumina.downsample_options(parser)
    parser.add_argument("config", type=str, help="config file")
    return parser


def main(args=None):
    if args is None:
        args = get_parser().parse_args()  # pragma: no cover
    config = AssemblerConfig.from_json(args.config, args.threads)
    workflows.run_workflows(args, config)
