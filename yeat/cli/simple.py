# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import cli, illumina
from argparse import ArgumentParser
import json
from pathlib import Path
from yeat import workflow


def main(args=None):
    if args is None:
        args = get_parser().parse_args()  # pragma: no cover
    create_config(args)
    add_config(args)
    setattr(args, "grid", False)
    workflow.run_workflow(args)


def get_parser(exit_on_error=True):
    parser = ArgumentParser(exit_on_error=exit_on_error)
    parser._optionals.title = "options"
    cli.workflow_configuration(parser)
    illumina.fastp_configuration(parser)
    illumina.downsample_configuration(parser)
    sample_configuration(parser)
    algorithm_configuration(parser)
    positional_args(parser)
    return parser


def sample_configuration(parser):
    sample = parser.add_argument_group("sample configuration")
    sample.add_argument(
        "--sample-label",
        default="sample1",
        help='set the sample label; by default, "sample1"',
        metavar="STR",
    )


def algorithm_configuration(parser):
    algorithm = parser.add_argument_group("algorithm configuration")
    algorithm.add_argument(
        "--assembly-label",
        default="assembly1",
        help='set the assembly label; by default, "assembly1"',
        metavar="STR",
    )
    group = algorithm.add_mutually_exclusive_group()
    group.add_argument(
        "--megahit",
        action="store_const",
        const=True,
        help="use MEGAHIT assembly algorithm; by default, SPAdes",
    )
    group.add_argument(
        "--unicycler",
        action="store_const",
        const=True,
        help="use Unicycler assembly algorithm; by default, SPAdes",
    )
    algorithm.add_argument(
        "--extra-args",
        default="",
        help='add assembly algorithm flags; for example, "--meta" or "--isolate --careful" for SPAdes; by default, empty string',
        metavar="STR",
    )


def positional_args(parser):
    parser._positionals.title = "required arguments"
    parser.add_argument("reads", type=str, nargs=2, help="paired-end reads in FASTQ format")


def create_config(args):
    data = {
        "samples": {args.sample_label: {"paired": [args.reads]}},
        "assemblies": {
            args.assembly_label: {
                "algorithm": get_algorithm(args),
                "extra_args": args.extra_args,
                "samples": [args.sample_label],
                "mode": "paired",
            }
        },
    }
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = open(outdir / "config.cfg", "w")
    json.dump(data, outfile, indent=4)


def get_algorithm(args):
    if args.megahit:
        return "megahit"
    elif args.unicycler:
        return "unicycler"
    else:
        return "spades"


def add_config(args):
    config = Path(args.outdir) / "config.cfg"
    setattr(args, "config", str(config.resolve()))
