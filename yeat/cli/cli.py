# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import downsample
from .config import AssemblerConfig
from argparse import Action, ArgumentParser
import json
import sys
import yeat
from yeat.workflows import workflows


CONFIG_TEMPLATE = {
    "samples": {
        "sample1": ["path_to_read1", "path_to_read2"],
        "sample2": ["path_to_read1", "path_to_read2"],
        "sample3": ["path_to_read"],
    },
    "assemblers": [
        {
            "label": "spades-meta",
            "algorithm": "spades",
            "extra_args": "--meta",
            "samples": ["sample1"],
        },
        {
            "label": "megahit-mins",
            "algorithm": "megahit",
            "extra_args": "--min-count 5 --min-contig-len 300",
            "samples": ["sample1", "sample2"],
        },
        {
            "label": "pacbio-hifi",
            "algorithm": "canu",
            "extra_args": "genomeSize=4.8m",
            "samples": ["sample3"],
        },
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
    downsample.options(parser)
    parser.add_argument("config", type=str, help="config file")
    return parser


def main(args=None):
    if args is None:
        args = get_parser().parse_args()  # pragma: no cover
    samples, assembly_configs = AssemblerConfig.parse_json(open(args.config))
    workflows.run_workflows(args, samples, assembly_configs)
