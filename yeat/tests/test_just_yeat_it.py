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
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
    ]
    run_yeat(arglist)


@pytest.mark.long
def test_paired_end_assemblers(capsys, tmp_path):
    wd = str(tmp_path)
    arglist = [
        "-w",
        wd,
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
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
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
    ]
    with pytest.raises(SystemExit, match="2"):
        run_yeat(arglist)
    captured = capsys.readouterr()
    message = (
        "argument --algorithm: invalid choice: 'DNE' (choose from spades, megahit, unicycler)"
    )
    assert message in captured.err
