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
from yeat.tests import data_file, get_core_count


def test_pacbio_hifi_assemblers_dry_run(tmp_path):
    wd = str(tmp_path)
    arglist = [
        "--outdir",
        wd,
        "-n",
        "-t",
        "4",
        data_file("configs/pacbio.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)


@pytest.mark.hifi
@pytest.mark.parametrize(
    "algorithm,label,expected",
    [
        ("canu", "canu-default", "sample1.contigs.fasta"),
        # ("flye", "flye-default", "assembly.fasta"),
    ],
)
def test_pacbio_hifi_read_assemblers(algorithm, label, expected, capsys, tmp_path):
    wd = str(tmp_path)
    cores = str(get_core_count())
    arglist = [
        "--outdir",
        wd,
        "--threads",
        cores,
        data_file(f"configs/{algorithm}.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    observed = Path(wd).resolve() / "analysis" / "sample1" / label / algorithm / expected
    assert observed.exists()
