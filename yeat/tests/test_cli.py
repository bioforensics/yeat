# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import argparse
import json
import pandas as pd
from pathlib import Path
import pytest
from yeat import cli
from yeat.cli import InitAction
from yeat.tests import data_file


def test_display_config_template(capsys):
    with pytest.raises(SystemExit):
        InitAction.__call__(None, None, None, None)
    out, err = capsys.readouterr()
    assert json.loads(out) == cli.CONFIG_TEMPLATE


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
    with pytest.raises(Exception, match=r"yeat is not an integer"):
        cli.main(None)


def test_invalid_read1_file():
    with pytest.raises(Exception, match=r"No such file:.*read1\'"):
        read1 = "read1"
        read2 = "read2"
        assemblers = ["spades"]
        cli.run(read1, read2, assemblers)


def test_invalid_read2_file():
    with pytest.raises(Exception, match=r"No such file:.*read2\'"):
        read1 = data_file("short_reads_1.fastq.gz")
        read2 = "read2"
        assemblers = ["spades"]
        cli.run(read1, read2, assemblers)


@pytest.mark.long
def test_multiple_assemblers(capsys, tmp_path):
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


@pytest.mark.long
def test_unicycler(capsys, tmp_path):
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


@pytest.mark.long
@pytest.mark.parametrize(
    "downsample,num_contigs,largest_contig,total_len",
    [("2000", 71, 5120, 69189), ("-1", 56, 35168, 199940)],
)
def test_custom_downsample_input(
    downsample, num_contigs, largest_contig, total_len, capsys, tmp_path
):
    wd = str(tmp_path)
    arglist = [
        data_file("megahit.cfg"),
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
        "--outdir",
        wd,
        "-d",
        downsample,
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    quast_report = Path(wd).resolve() / "analysis" / "quast" / "megahit" / "report.tsv"
    df = pd.read_csv(quast_report, sep="\t")
    assert df.iloc[12]["sample_contigs"] == num_contigs
    assert df.iloc[13]["sample_contigs"] == largest_contig
    assert df.iloc[14]["sample_contigs"] == total_len


@pytest.mark.parametrize("coverage", [("-1"), ("0")])
def test_invalid_custom_coverage_1(coverage):
    arglist = [
        data_file("megahit.cfg"),
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
        "--coverage",
        coverage,
    ]
    with pytest.raises(SystemExit) as e:
        args = cli.get_parser().parse_args(arglist)
    assert isinstance(e.value.__context__, argparse.ArgumentError)
    assert f"{coverage} is not a positive integer" in e.value.__context__.message


@pytest.mark.parametrize("coverage", [("string"), ("3.14")])
def test_invalid_custom_coverage_2(coverage):
    arglist = [
        data_file("megahit.cfg"),
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
        "--coverage",
        coverage,
    ]
    with pytest.raises(Exception, match=r"is not an integer"):
        args = cli.get_parser().parse_args(arglist)


@pytest.mark.long
@pytest.mark.parametrize(
    "coverage,num_contigs,largest_contig,total_len",
    [("125", 56, 35168, 199940), ("150", 56, 35168, 199940)],
)
def test_custom_coverage_input(coverage, num_contigs, largest_contig, total_len, capsys, tmp_path):
    wd = str(tmp_path)
    arglist = [
        data_file("megahit.cfg"),
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
        "--outdir",
        wd,
        "-c",
        coverage,
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    quast_report = Path(wd).resolve() / "analysis" / "quast" / "megahit" / "report.tsv"
    df = pd.read_csv(quast_report, sep="\t")
    assert df.iloc[12]["sample_contigs"] == num_contigs
    assert df.iloc[13]["sample_contigs"] == largest_contig
    assert df.iloc[14]["sample_contigs"] == total_len
