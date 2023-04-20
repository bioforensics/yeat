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
from yeat.bandage import bandage
from yeat.workflows import workflows


CONFIG_TEMPLATE = [
    dict(
        algorithm="spades",
        extra_args="--meta",
    ),
    dict(
        algorithm="megahit",
        extra_args="--min-count 5 --min-contig-len 300",
    ),
]


class InitAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        json.dump(CONFIG_TEMPLATE, sys.stdout, indent=4)
        print()
        raise SystemExit()


def options(parser):
    parser.add_argument(
        "--init",
        action=InitAction,
        nargs=0,
        help="print a template assembly config file to the terminal (stdout) and exit",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="construct workflow DAG and print a summary but do not execute",
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
        "--sample",
        type=str,
        metavar="S",
        default="sample",
        help="specify a unique sample name S for storing assembly results in the working directory; by default S=sample",
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        metavar="T",
        default=1,
        help="execute workflow with T threads; by default T=1",
    )
    parser.add_argument("-v", "--version", action="version", version=f"YEAT v{yeat.__version__}")


def read_input_types(parser):
    read_input_options = parser.add_argument_group("input read options")
    mx = read_input_options.add_mutually_exclusive_group(required=True)
    mx.add_argument(
        "--paired",
        metavar=("READ1", "READ2"),
        type=str,
        nargs=2,
        help="paired-end reads in FASTQ format",
    )
    mx.add_argument("--pacbio", metavar="READ", type=str, help="PacBio HiFi-reads in FASTQ format")


def get_parser(exit_on_error=True):
    parser = ArgumentParser(exit_on_error=exit_on_error)
    options(parser)
    downsample.options(parser)
    read_input_types(parser)
    parser.add_argument("config", type=str, help="config file")
    return parser


def main(args=None):
    if args is None:
        args = get_parser().parse_args()
    assembly_configs = AssemblerConfig.parse_json(open(args.config))
    workflows.run_workflow(args, assembly_configs)
    if not args.dry_run:
        bandage.run_bandage(
            assembly_configs=assembly_configs, outdir=args.outdir, cores=args.threads
        )
