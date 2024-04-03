# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .auto_pop import AutoPop
from argparse import ArgumentParser


def main(args=None):
    if args is None:
        args = get_parser().parse_args()  # pragma: no cover
    AutoPop(args)


def get_parser(exit_on_error=True):
    parser = ArgumentParser(exit_on_error=exit_on_error)
    parser._optionals.title = "options"
    config_configuration(parser)
    input_configuration(parser)
    positional_args(parser)
    return parser


def config_configuration(parser):
    config = parser.add_argument_group("config configuration")
    config.add_argument(
        "-o",
        "--outfile",
        default="config.cfg",
        help='output config file; by default, "config.cfg"',
        metavar="FILE",
        type=str,
    )


def input_configuration(parser):
    ingrp = parser.add_argument_group("input configuration")
    meg = ingrp.add_mutually_exclusive_group()
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
