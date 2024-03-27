# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pathlib import Path
import pytest
from yeat.cli.just_yeat_it import get_parser, main
from yeat.tests import data_file, target_files_exist


def run_yeat(arglist):
    args = get_parser().parse_args(arglist)
    main(args)


@pytest.mark.short
def test_paired_end_assemblers_dry_run(tmp_path):
    wd = str(tmp_path)
    arglist = [
        "-o",
        wd,
        "-n",
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
    ]
    run_yeat(arglist)


@pytest.mark.long
@pytest.mark.illumina
@pytest.mark.parametrize("algorithm", ["spades", "megahit", "unicycler"])
def test_paired_end_assemblers(algorithm, capsys, tmp_path):
    wd = str(tmp_path)
    arglist = [
        "-o",
        wd,
        "--algorithm",
        algorithm,
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
    ]
    run_yeat(arglist)
    config = str((Path(wd) / "config.cfg").resolve())
    target_files_exist(wd, config)


@pytest.mark.short
def test_missing_second_input_read(capsys, tmp_path):
    wd = str(tmp_path)
    arglist = ["-o", wd, data_file("short_reads_1.fastq.gz")]
    with pytest.raises(SystemExit):
        get_parser().parse_args(arglist)
    out, err = capsys.readouterr()
    assert "error: the following arguments are required: reads" in err


@pytest.mark.short
def test_invalid_input_algorithm(capsys, tmp_path):
    wd = str(tmp_path)
    arglist = [
        "-o",
        wd,
        "--algorithm",
        "INVALID",
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
    ]
    with pytest.raises(RuntimeError, match="Snakemake Failed"):
        run_yeat(arglist)
    out, err = capsys.readouterr()
    assert "Invalid assembly algorithm 'INVALID' for 'assembly1'" in err
