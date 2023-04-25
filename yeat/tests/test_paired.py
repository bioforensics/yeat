# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pandas as pd
from pathlib import Path
import pytest
import re
import subprocess
from yeat import cli, workflows
from yeat.tests import data_file


def test_paired_end_read_assemblers_dry_run(tmp_path):
    """The purpose of this test is to check if the snakemake workflow is properly defined."""
    wd = str(tmp_path)
    arglist = [
        "--outdir",
        wd,
        "--sample",
        "Animal_289",
        "-n",
        "--paired",
        data_file("Animal_289_R1.fq.gz"),
        data_file("Animal_289_R2.fq.gz"),
        data_file("config.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)


def test_invalid_read1_file():
    with pytest.raises(Exception, match=r"No such file:.*read1\'"):
        read1 = "read1"
        read2 = "read2"
        assemblers = ["spades"]
        workflows.run_paired(read1, read2, assemblers)


def test_invalid_read2_file():
    with pytest.raises(Exception, match=r"No such file:.*read2\'"):
        read1 = data_file("short_reads_1.fastq.gz")
        read2 = "read2"
        assemblers = ["spades"]
        workflows.run_paired(read1, read2, assemblers)


@pytest.mark.long
def test_multiple_assemblers(capsys, tmp_path):
    wd = str(tmp_path)
    arglist = [
        "--outdir",
        wd,
        "--paired",
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
        data_file("config.cfg"),
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
        "--outdir",
        wd,
        "--paired",
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
        data_file("unicycler.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    assembly_result = Path(wd).resolve() / "analysis" / "unicycler" / "assembly.fasta"
    assert assembly_result.exists()


@pytest.mark.long
@pytest.mark.parametrize(
    "downsample,num_contigs,largest_contig,total_len",
    [("2000", 79, 5294, 70818), ("-1", 56, 35168, 199940)],
)
def test_custom_downsample_input(
    downsample, num_contigs, largest_contig, total_len, capsys, tmp_path
):
    wd = str(tmp_path)
    arglist = [
        "--outdir",
        wd,
        "-d",
        downsample,
        "--seed",
        "0",
        "--paired",
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
        data_file("megahit.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    quast_report = Path(wd).resolve() / "analysis" / "quast" / "megahit" / "report.tsv"
    df = pd.read_csv(quast_report, sep="\t")
    assert df.iloc[12]["sample_contigs"] == num_contigs
    assert df.iloc[13]["sample_contigs"] == largest_contig
    assert df.iloc[14]["sample_contigs"] == total_len


@pytest.mark.long
@pytest.mark.parametrize("execution_number", range(3))
def test_random_downsample_seed(execution_number, capsys, tmp_path):
    wd = str(tmp_path)
    arglist = [
        "--outdir",
        wd,
        "-d",
        "2000",
        "--paired",
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
        data_file("megahit.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    quast_report = Path(wd).resolve() / "analysis" / "quast" / "megahit" / "report.tsv"
    df = pd.read_csv(quast_report, sep="\t")
    num_contigs = df.iloc[12]["sample_contigs"]
    assert num_contigs == pytest.approx(76, abs=15)  # 76 +/- 20%
    largest_contig = df.iloc[13]["sample_contigs"]
    assert largest_contig == pytest.approx(5228, abs=1045)  # 5228 +/- 20%
    total_len = df.iloc[14]["sample_contigs"]
    assert total_len == pytest.approx(74393, abs=14878)  # 74393 +/- 20%


def prep_uncompressed_reads(filename, tmp_path):
    if filename.endswith(".gz"):
        return data_file(filename)
    datadir = tmp_path / "data"
    datadir.mkdir(parents=True, exist_ok=True)
    gzfile = data_file(f"{filename}.gz")
    ungzfile = datadir / filename
    with open(ungzfile, "w") as fh:
        subprocess.run(["gunzip", "-c", gzfile], stdout=fh)
    return str(ungzfile)


@pytest.mark.long
@pytest.mark.parametrize(
    "inread1,inread2",
    [
        ("short_reads_1.fastq", "short_reads_2.fastq"),
        ("short_reads_1.fastq.gz", "short_reads_2.fastq"),
    ],
)
def test_uncompressed_input_reads(inread1, inread2, capfd, tmp_path):
    wd = tmp_path / "wd"
    inread1 = prep_uncompressed_reads(inread1, tmp_path)
    inread2 = prep_uncompressed_reads(inread2, tmp_path)
    arglist = [
        "--outdir",
        str(wd),
        "--paired",
        inread1,
        inread2,
        data_file("megahit.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    outread1 = wd / "seq" / "input" / "sample_R1.fq.gz"
    outread2 = wd / "seq" / "input" / "sample_R2.fq.gz"
    assert outread1.exists()
    assert outread2.exists()
    subprocess.run(["gzip", "-tv", outread1, outread2])
    captured = capfd.readouterr()
    assert re.search(r"seq/input/sample_R1.fq.gz:\s*OK", captured.err)
    assert re.search(r"seq/input/sample_R2.fq.gz:\s*OK", captured.err)


@pytest.mark.long
@pytest.mark.parametrize("coverage", [("150"), ("75"), ("10")])
def test_custom_coverage_input(coverage, capsys, tmp_path):
    wd = str(tmp_path)
    arglist = [
        "--outdir",
        wd,
        "-c",
        coverage,
        "--paired",
        data_file("short_reads_1.fastq.gz"),
        data_file("short_reads_2.fastq.gz"),
        data_file("megahit.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    quast_report = Path(wd).resolve() / "analysis" / "quast" / "megahit" / "report.tsv"
    df = pd.read_csv(quast_report, sep="\t")
    num_contigs = df.iloc[12]["sample_contigs"]
    assert num_contigs == 56
    largest_contig = df.iloc[13]["sample_contigs"]
    assert largest_contig == 35168
    total_len = df.iloc[14]["sample_contigs"]
    assert total_len == 199940