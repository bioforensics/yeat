# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------


def cli(subparsers):
    parser_long = subparsers.add_parser("long", help="long-reads")
    mx = parser_long.add_mutually_exclusive_group(required=True)
    mx.add_argument("--pacbio", metavar="READ", type=str, help="PacBio reads in FASTQ format")
    # mx.add_argument("--nanopore", metavar="READ", type=str, help="Nanopore reads in FASTQ format")
    # mx.add_argument("--sanger", metavar="READ", type=str, help="Sanger reads in FASTQ format")
