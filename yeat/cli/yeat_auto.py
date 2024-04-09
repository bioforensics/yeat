# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from argparse import ArgumentParser
from yeat.config.auto_pop import AutoPop


def main(args=None):
    if args is None:
        args = get_parser().parse_args()  # pragma: no cover
    autopop = AutoPop(args.samples, args.seq_path, args.files)
    autopop.write_config_file()


def get_parser(exit_on_error=True):
    parser = ArgumentParser(exit_on_error=exit_on_error)
    options(parser)
    positional_args(parser)
    return parser


def options(parser):
    parser._optionals.title = "options"
    meg = parser.add_mutually_exclusive_group(required=True)
    meg.add_argument(
        "--seq-path",
        default=None,
        help="path to a directory containing FASTQ files to use as input; incompatible with --files",
        metavar="PATH",
    )
    meg.add_argument(
        "--files",
        default=None,
        help="a list of FASTQ files to use as input; incompatible with --seq-path",
        metavar="FQ",
        nargs="+",
    )


def positional_args(parser):
    parser._positionals.title = "required arguments"
    parser.add_argument(
        "samples",
        help="list of sample names or path to .txt file containing sample names",
        nargs="+",
    )
