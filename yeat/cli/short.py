# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from argparse import ArgumentTypeError


def check_positive(value):
    try:
        value = int(value)
        if value <= 0:
            raise ArgumentTypeError(f"{value} is not a positive integer")
    except ValueError:
        raise ArgumentTypeError(f"{value} is not an integer")
    return value


def options(parser):
    parser.add_argument(
        "-c",
        "--coverage",
        type=check_positive,
        metavar="C",
        default=150,
        help="target an average depth of coverage Cx when auto-downsampling; by default, C=150",
    )
    parser.add_argument(
        "-d",
        "--downsample",
        type=int,
        metavar="D",
        default=0,
        help="randomly sample D reads from the input rather than assembling the full set; set D=0 to perform auto-downsampling to a desired level of coverage (see --coverage); set D=-1 to disable downsampling; by default D=0",
    )
    parser.add_argument(
        "-g",
        "--genome-size",
        type=int,
        metavar="G",
        default=0,
        help="provide known genome size in base pairs (bp); by default, G=0",
    )
    parser.add_argument(
        "--seed",
        type=int,
        metavar="S",
        default=None,
        help="seed for the random number generator used for downsampling; by default the seed is chosen randomly",
    )


def cli(subparsers):
    parser_short = subparsers.add_parser("short", help="short-reads")
    options(parser_short)
    mx = parser_short.add_mutually_exclusive_group(required=True)
    mx.add_argument(
        "--paired",
        metavar=("READ1", "READ2"),
        type=str,
        nargs=2,
        help="paired-end reads in FASTQ format",
    )
    # mx.add_argument("--single", metavar="READ", type=str, help="single-end reads in FASTQ format")
    # mx.add_argument("--interleaved", metavar="READ", type=str, help="interleaved-paired-end reads in FASTQ format")
