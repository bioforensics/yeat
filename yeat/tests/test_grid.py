# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
from yeat import workflow
from yeat.cli import cli
from yeat.tests import *


@pytest.mark.short
@pytest.mark.parametrize(
    "arglist,expected",
    [
        (["-t", "200", data_file("configs/single.cfg")], " -V -pe threads 200 "),
        (
            ["--grid-args", " -q largemem -p -1000 ", data_file("configs/single.cfg")],
            " -q largemem -p -1000 ",
        ),
        ([data_file("configs/single.cfg")], " -V "),
    ],
)
def test_setup_grid_args(arglist, expected):
    args = cli.get_parser().parse_args(arglist)
    observed = workflow.setup_grid_args(args)
    assert observed == expected


@pytest.mark.grid
def test_grid(tmp_path):
    wd = str(tmp_path)
    arglist = ["-o", wd, "-t", "200", "--grid", data_file("configs/single.cfg")]
    run_yeat(arglist)
    expected = [
        "analysis/Shigella_sonnei_53G/single/spades-default/spades/contigs.fasta",
        "analysis/Shigella_sonnei_53G/single/megahit-default/megahit/contigs.fasta",
        "analysis/Shigella_sonnei_53G/single/unicycler-default/unicycler/contigs.fasta",
    ]
    for contig in expected:
        assert (Path(wd) / contig).exists()
