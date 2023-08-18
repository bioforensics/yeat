# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pathlib import Path
import pytest
from yeat import cli
from yeat.tests import data_file, write_config, files_exists


def test_single_end_assemblers_dry_run(tmp_path):
    wd = str(tmp_path)
    arglist = ["-o", wd, "-n", data_file("configs/single.cfg")]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)


@pytest.mark.long
@pytest.mark.parametrize(
    "labels,expected",
    [
        (["spades-default"], "contigs.fasta"),
        (["megahit-default"], "final.contigs.fa"),
        (["unicycler-default"], "assembly.fasta"),
    ],
)
def test_single_end_assemblers(labels, expected, capsys, tmp_path):
    wd = str(tmp_path)
    assemblers = write_config(labels, wd, "single.cfg")
    cfg = str(Path(wd) / "single.cfg")
    arglist = ["-o", wd, cfg]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    files_exists(wd, assemblers, expected)
