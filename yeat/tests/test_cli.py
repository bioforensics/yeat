# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import json
import pytest
from yeat import cli
from yeat.assembly.config import AssemblyConfiguration
from yeat.tests import data_file


# the purpose of this test is to check if the snakemake workflow is properly defined.
def test_basic_dry_run(tmp_path):
    wd = str(tmp_path)
    arglist = [
        data_file("config.cfg"),
        data_file("Animal_289_R1.fq.gz"),
        data_file("Animal_289_R2.fq.gz"),
        "--outdir",
        wd,
        "--sample",
        "Animal_289",
        "-n",
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)


def test_no_args():
    with pytest.raises(SystemExit, match=r"2"):
        cli.main(None)


def test_snakemake_fail_because_of_invalid_read_files():
    with pytest.raises(Exception, match=r"Snakemake Failed"):
        read1 = "read1"
        read2 = "read2"
        assembler = AssemblyConfiguration("assembly1", "spades")
        cli.run(read1, read2, assembler)


def test_init_flag(capsys):
    parser = cli.get_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--init"])
    terminal = capsys.readouterr()
    obs_out = json.loads(terminal.out)
    expected_out = [
        {"label": "assembly1", "algorithm": "spades"},
        {"label": "assembly2", "algorithm": "megahit"},
    ]
    assert obs_out == expected_out
