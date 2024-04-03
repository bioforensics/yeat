# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
from yeat.cli.yeat_auto import get_parser, main
from yeat.tests import data_file


def run_yeat_auto(arglist):
    args = get_parser().parse_args(arglist)
    main(args)


@pytest.mark.short
def test_yeat_auto(tmp_path):
    wd = str(tmp_path)
    arglist = [
        "short_reads",
        "--files",
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
        "-o",
        f"{wd}/config.cfg",
    ]
    run_yeat_auto(arglist)
    print(wd)
    assert 0


# test one sample
# test two samples
# test sample.txt
# test --seq-path bad path
# test --seq-path no path
# test --seq-path good
# test --files no files
# test --files one file
# test --files bad first file
# test --files bad second file
# test --files good
