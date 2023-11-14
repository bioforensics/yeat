# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from argparse import ArgumentTypeError


def fastp_options(parser):
    illumina = parser.add_argument_group("fastp arguments")
    illumina.add_argument(
        "-l",
        "--length-required",
        default=50,
        help="discard reads shorter than the required L length after pre-preocessing; by default, L=50",
        metavar="L",
        type=int,
    )


def downsample_options(parser):
    illumina = parser.add_argument_group("downsample arguments")
    illumina.add_argument(
        "-c",
        "--coverage",
        default=150,
        help="target an average depth of coverage Cx when auto-downsampling; by default, C=150",
        metavar="C",
        type=check_positive,
    )
    illumina.add_argument(
        "-d",
        "--downsample",
        default=0,
        help="randomly sample D reads from the input rather than assembling the full set; set D=0 to perform auto-downsampling to a desired level of coverage (see --coverage); set D=-1 to disable downsampling; by default, D=0",
        metavar="D",
        type=int,
    )
    illumina.add_argument(
        "-g",
        "--genome-size",
        default=0,
        help="provide known genome size in base pairs (bp); by default, G=0",
        metavar="G",
        type=int,
    )
    illumina.add_argument(
        "-s",
        "--seed",
        default=None,
        help="seed for the random number generator used for downsampling; by default, the seed is chosen randomly",
        metavar="S",
        type=int,
    )


def check_positive(value):
    try:
        value = int(value)
        if value <= 0:
            raise ArgumentTypeError(f"{value} is not a positive integer")
    except ValueError:
        raise ArgumentTypeError(f"{value} is not an integer")
    return value
