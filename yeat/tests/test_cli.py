# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pathlib import Path
import pytest
import yeat
from yeat import cli
from yeat.tests import data_file


# the purpose of this test is to check if the snakemake workflow is properly defined.
def test_basic_dry_run(tmp_path):
    wd = str(tmp_path)
    arglist = [
        data_file("Animal_289_R1.fq.gz"),
        data_file("Animal_289_R2.fq.gz"),
        "--assemblers",
        "spades",
        "--outdir",
        wd,
        "--sample",
        "Animal_289",
        "-n",
    ]
    args = yeat.cli.get_parser().parse_args(arglist)
    yeat.cli.main(args)


def test_no_args():
    with pytest.raises(SystemExit, match=r"2"):
        yeat.cli.main(None)


def test_snakemake_fail_because_of_invalid_read_files():
    with pytest.raises(Exception, match=r"Snakemake Failed"):
        read1 = "read1"
        read2 = "read2"
        assemblers = "spades"
        yeat.cli.run(read1, read2, assemblers)


def test_unsupported_assembly_algorithm():
    assemblers = ["unsupported_assembly"]
    error_message = r"Found unsupported assembly algorithm with `--assemblers` flag: \[\[unsupported_assembly\]\]!"
    with pytest.raises(ValueError, match=error_message):
        yeat.cli.check_assemblers(assemblers)


def test_duplicate_assembly_algorithms():
    assemblers = ["spades", "spades"]
    error_message = r"Found duplicate assembly algorithm with `--assemblers` flag: \[\[spades\]\]!"
    with pytest.raises(ValueError, match=error_message):
        yeat.cli.check_assemblers(assemblers)


def test_unicycler(capsys, tmp_path):
    wd = str(tmp_path)
    arglist = [
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
        "--assemblers",
        "unicycler",
        "--outdir",
        wd,
    ]
    args = yeat.cli.get_parser().parse_args(arglist)
    yeat.cli.main(args)
    assembly_result = Path(wd).resolve() / "analysis" / "unicycler" / "assembly.fasta"
    assert assembly_result.exists()
