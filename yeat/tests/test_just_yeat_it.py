# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from argparse import ArgumentError
from pathlib import Path
import pytest
from yeat.cli.just_yeat_it import get_parser, main, check_positive
from yeat.tests import data_file, final_contig_files_exist


def run_yeat(arglist):
    args = get_parser().parse_args(arglist)
    main(args)


def test_paired_end_assemblers_dry_run(tmp_path):
    wd = str(tmp_path)
    arglist = [
        "-w",
        wd,
        "-n",
        data_file("short_reads_?.fastq.gz"),
    ]
    run_yeat(arglist)


@pytest.mark.long
@pytest.mark.parametrize("algorithm", ["spades", "megahit", "unicycler", "penguin", "velvet"])
def test_paired_end_assemblers(algorithm, capsys, tmp_path):
    wd = str(tmp_path)
    arglist = [
        "-w",
        wd,
        "--algorithm",
        algorithm,
        data_file("short_reads_?.fastq.gz"),
    ]
    run_yeat(arglist)
    config = str((Path(wd) / "config.toml").resolve())
    final_contig_files_exist(wd, config)


def test_invalid_input_algorithm(capsys, tmp_path):
    wd = str(tmp_path)
    arglist = [
        "-w",
        wd,
        "--algorithm",
        "DNE",
        data_file("short_reads_?.fastq.gz"),
    ]
    with pytest.raises(RuntimeError, match="Snakemake Failed"):
        run_yeat(arglist)
    out, err = capsys.readouterr()
    assert "Unknown assembly algorithm DNE" in err


@pytest.mark.parametrize("value", [1, 10, 100])
def test_check_positive_valid_values(value):
    check_positive(value) == value


@pytest.mark.parametrize("target_coverage_depth", [("-1"), ("0")])
def test_invalid_target_coverage_depth_negative(target_coverage_depth):
    arglist = ["-c", target_coverage_depth, data_file("paired.toml")]
    with pytest.raises(ArgumentError, match=rf"{target_coverage_depth} is not a positive integer"):
        get_parser(exit_on_error=False).parse_args(arglist)


@pytest.mark.parametrize("target_coverage_depth", [("string"), ("3.14")])
def test_invalid_target_coverage_depth_noninteger(target_coverage_depth):
    arglist = ["-c", target_coverage_depth, data_file("paired.toml")]
    with pytest.raises(ArgumentError, match=rf"{target_coverage_depth} is not an integer"):
        get_parser(exit_on_error=False).parse_args(arglist)
