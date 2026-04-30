# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
from yeat.workflow.qc.downsample import Downsample
from yeat.tests import data_file


def test_downsample():
    Downsample.parse_data(
        target_depth=150,
        target_num_reads="auto",
        genome_size="auto",
        mash_report=data_file("mash_report.tsv"),
        seqkit_report=data_file("seqkit_report.tsv"),
        read_type="paired",
    )


def test_get_genome_size():
    report_path = data_file("mash_report.tsv")
    genome_size = Downsample._get_estimated_genome_size(report_path)
    assert genome_size == 188786


def test_get_average_read_length():
    report_path = data_file("seqkit_report.tsv")
    average_read_length = Downsample._get_average_read_length(report_path)
    assert average_read_length == 125.0


@pytest.mark.parametrize("input_down", [0, 3765000])
def test_get_num_reads(input_down):
    downsample = Downsample(
        target_depth=150,
        target_num_reads=input_down,
        genome_size=6275000,
        average_read_length=125.0,
        read_type="paired",
    )
    down = downsample.target_num_reads
    assert down == 3765000
