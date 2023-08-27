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
from yeat.tests import data_file, get_core_count, write_config, files_exists


def test_oxford_nanopore_assemblers_dry_run(tmp_path):
    wd = str(tmp_path)
    arglist = ["-o", wd, "-n", "-t", "4", data_file("configs/ont.cfg")]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)


@pytest.mark.nano
@pytest.mark.parametrize(
    "labels,expected",
    [
        (["flye-default"], "assembly.fasta"),
        (["canu-default"], "Ecoli_K12_MG1655_R10.3_HAC.contigs.fasta"),
        (["unicycler-default"], "assembly.fasta"),
    ],
)
def test_oxford_nanopore_read_assemblers(labels, expected, capsys, tmp_path):
    wd = str(tmp_path)
    assemblers = write_config(labels, wd, "ont.cfg")
    cores = str(get_core_count())
    cfg = str(Path(wd) / "ont.cfg")
    arglist = ["-o", wd, "-t", cores, cfg]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    files_exists(wd, assemblers, expected)
