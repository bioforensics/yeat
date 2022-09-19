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
from yeat import cli
from yeat.tests import data_file


def test_basic_dry_run(tmp_path):
    """The purpose of this test is to check if the snakemake workflow is properly defined."""
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


def test_invalid_read_files():
    with pytest.raises(Exception, match=r"No such file:.*read1\'"):
        read1 = "read1"
        read2 = "read2"
        assemblers = ["spades"]
        cli.run(read1, read2, assemblers)


def test_multiple_assemblers(tmp_path):
    wd = str(tmp_path)
    arglist = [
        data_file("config.cfg"),
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
        "--outdir",
        wd,
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    spades_result = Path(wd).resolve() / "analysis" / "spades" / "contigs.fasta"
    assert spades_result.exists()
    megahit_result = Path(wd).resolve() / "analysis" / "megahit" / "final.contigs.fa"
    assert megahit_result.exists()


def test_unicycler(tmp_path):
    wd = str(tmp_path)
    arglist = [
        data_file("unicycler.cfg"),
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
        "--outdir",
        wd,
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    assembly_result = Path(wd).resolve() / "analysis" / "unicycler" / "assembly.fasta"
    assert assembly_result.exists()
