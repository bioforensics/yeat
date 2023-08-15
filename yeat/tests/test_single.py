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
from yeat.tests import data_file


def test_single_end_assemblers_dry_run(tmp_path):
    wd = str(tmp_path)
    arglist = [
        "--outdir",
        wd,
        "-n",
        data_file("configs/single.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)


# @pytest.mark.long
# @pytest.mark.parametrize(
#     "algorithm,label,expected",
#     [
#         ("spades", "spades-meta", "contigs.fasta"),
#         ("megahit", "megahit-default", "final.contigs.fa"),
#         ("unicycler", "unicycler-default", "assembly.fasta"),
#     ],
# )
# def test_individual_single_end_assemblers(algorithm, label, expected, capsys, tmp_path):
#     wd = str(tmp_path)
#     arglist = [
#         "--outdir",
#         wd,
#         data_file(f"configs/{algorithm}.cfg"),
#     ]
#     args = cli.get_parser().parse_args(arglist)
#     cli.main(args)
#     analysis_dir = Path(wd).resolve() / "analysis"
#     assert (analysis_dir / "sample1" / label / algorithm / expected).exists()
