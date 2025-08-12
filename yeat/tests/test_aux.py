# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import numpy
import pytest
from yeat.tests import data_file
from yeat.workflow.qc.aux import (
    copy_input,
    get_genome_size,
    get_average_read_length,
    get_down,
    print_downsample_values,
)


@pytest.mark.parametrize("do_copy, expected_symlink", [(True, False), (False, True)])
def test_copy_input(tmp_path, do_copy, expected_symlink):
    src_file = data_file("short_reads_1.fastq.gz")
    dest_file = tmp_path / "short_reads_1.fastq.gz"
    copy_input(src_file, dest_file, do_copy)
    assert dest_file.exists()
    assert dest_file.is_symlink() == expected_symlink


@pytest.mark.parametrize("input_value", [0, numpy.int64(6275000)])
def test_get_genome_size(input_value):
    report_path = data_file("combined-reads.report.tsv")
    genome_size = get_genome_size(input_value, report_path)
    assert isinstance(genome_size, numpy.integer)
    assert genome_size > 0
    if input_value != 0:
        assert genome_size == input_value


def test_get_average_read_length():
    avg_read_length = get_average_read_length(data_file("fastp.json"))
    assert avg_read_length == 125.0


@pytest.mark.parametrize("downsample", [0, 3765000])
def test_get_down(downsample):
    genome_size = 6275000
    coverage_depth = 150
    avg_read_length = 125.0
    down = get_down(downsample, genome_size, coverage_depth, avg_read_length)
    assert isinstance(down, int)
    assert down >= 0
    if downsample != 0:
        assert down == downsample


def test_print_downsample_values(capsys):
    genome_size = 6275000
    avg_read_length = 125.0
    coverage_depth = 150
    down = 3765000
    seed = 802
    print_downsample_values(genome_size, avg_read_length, coverage_depth, down, seed)
    captured = capsys.readouterr()
    expected_output = (
        f"[yeat] genome size: {genome_size}\n"
        f"[yeat] average read length: {avg_read_length}\n"
        f"[yeat] target depth of coverage: {coverage_depth}x\n"
        f"[yeat] number of reads to sample: {down}\n"
        f"[yeat] random seed for sampling: {seed}\n"
    )
    assert captured.out == expected_output
