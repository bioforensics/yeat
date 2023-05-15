# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import json
import pandas as pd
from pathlib import Path
import pytest
import re
import subprocess
from yeat import cli
from yeat.tests import data_file


def test_paired_end_assemblers_dry_run(tmp_path):
    """The purpose of this test is to check if the snakemake workflow is properly defined."""
    wd = str(tmp_path)
    arglist = [
        "--outdir",
        wd,
        "-n",
        data_file("configs/paired.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)


@pytest.mark.long
@pytest.mark.parametrize(
    "algorithm,label,expected",
    [
        ("spades", "spades-meta", "contigs.fasta"),
        ("megahit", "megahit-default", "final.contigs.fa"),
        ("unicycler", "unicycler-default", "assembly.fasta"),
    ],
)
def test_individual_paired_end_assemblers(algorithm, label, expected, capsys, tmp_path):
    wd = str(tmp_path)
    arglist = [
        "--outdir",
        wd,
        data_file(f"configs/{algorithm}.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    observed = Path(wd).resolve() / "analysis" / "sample1" / label / algorithm / expected
    assert observed.exists()


@pytest.mark.long
def test_multiple_spades(capsys, tmp_path):
    wd = str(tmp_path)
    arglist = [
        "--outdir",
        wd,
        data_file(f"configs/two_spades.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    analysis_dir = Path(wd).resolve() / "analysis"
    expected = [
        analysis_dir / "sample1" / "spades-default" / "spades" / "contigs.fasta",
        analysis_dir / "sample1" / "spades-meta" / "spades" / "contigs.fasta",
    ]
    for observed in expected:
        assert observed.exists()


@pytest.mark.long
def test_multiple_paired_end_assemblers(capsys, tmp_path):
    wd = str(tmp_path)
    arglist = [
        "--outdir",
        wd,
        data_file(f"configs/unicycler_spades.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    analysis_dir = Path(wd).resolve() / "analysis"
    expected = [
        analysis_dir / "sample1" / "unicycler-default" / "unicycler" / "assembly.fasta",
        analysis_dir / "sample1" / "spades-meta" / "spades" / "contigs.fasta",
    ]
    for observed in expected:
        assert observed.exists()


# @pytest.mark.long
# def test_run_complex_paired_end_config(capsys, tmp_path):
#     wd = str(tmp_path)
#     arglist = [
#         "--outdir",
#         wd,
#         data_file("configs/paired.cfg"),
#     ]
#     args = cli.get_parser().parse_args(arglist)
#     cli.main(args)
#     analysis_dir = Path(wd).resolve() / "analysis"
#     expected = [
#         analysis_dir / "sample1" / "default_spades" / "spades" / "contigs.fasta",
#         analysis_dir / "sample2" / "default_spades" / "spades" / "contigs.fasta",
#         analysis_dir / "sample2" / "default_megahit" / "megahit" / "final.contigs.fa",
#         analysis_dir / "sample1" / "Shigella_sonnei_plasmids" / "unicycler" / "assembly.fasta",
#     ]
#     for observed in expected:
#         assert observed.exists()


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
        data_file("configs/megahit.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    analysis_dir = Path(wd).resolve() / "analysis"
    quast_report = (
        analysis_dir / "sample1" / "megahit-default" / "megahit" / "quast" / "report.tsv"
    )
    df = pd.read_csv(quast_report, sep="\t")
    assert df.iloc[12]["sample1_contigs"] == num_contigs
    assert df.iloc[13]["sample1_contigs"] == largest_contig
    assert df.iloc[14]["sample1_contigs"] == total_len


@pytest.mark.long
@pytest.mark.parametrize("coverage", [("150"), ("75"), ("10")])
def test_custom_coverage_input(coverage, capsys, tmp_path):
    wd = str(tmp_path)
    arglist = [
        "--outdir",
        wd,
        "-c",
        coverage,
        data_file("configs/megahit.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    analysis_dir = Path(wd).resolve() / "analysis"
    quast_report = (
        analysis_dir / "sample1" / "megahit-default" / "megahit" / "quast" / "report.tsv"
    )
    df = pd.read_csv(quast_report, sep="\t")
    num_contigs = df.iloc[12]["sample1_contigs"]
    assert num_contigs == 56
    largest_contig = df.iloc[13]["sample1_contigs"]
    assert largest_contig == 35168
    total_len = df.iloc[14]["sample1_contigs"]
    assert total_len == 199940


@pytest.mark.long
@pytest.mark.parametrize("execution_number", range(3))
def test_random_downsample_seed(execution_number, capsys, tmp_path):
    wd = str(tmp_path)
    arglist = [
        "--outdir",
        wd,
        "-d",
        "2000",
        data_file("configs/megahit.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    analysis_dir = Path(wd).resolve() / "analysis"
    quast_report = (
        analysis_dir / "sample1" / "megahit-default" / "megahit" / "quast" / "report.tsv"
    )
    df = pd.read_csv(quast_report, sep="\t")
    num_contigs = df.iloc[12]["sample1_contigs"]
    assert num_contigs == pytest.approx(76, abs=15)  # 76 +/- 20%
    largest_contig = df.iloc[13]["sample1_contigs"]
    assert largest_contig == pytest.approx(5228, abs=1045)  # 5228 +/- 20%
    total_len = df.iloc[14]["sample1_contigs"]
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
    wd = str(tmp_path)
    inread1 = prep_uncompressed_reads(inread1, tmp_path)
    inread2 = prep_uncompressed_reads(inread2, tmp_path)
    cfg_data = json.load(open(data_file("configs/megahit.cfg")))
    cfg_data["samples"]["sample1"] = [inread1, inread2]
    cfg = str(Path(wd).resolve() / "megahit.cfg")
    json.dump(cfg_data, open(cfg, "w"))
    arglist = [
        "--outdir",
        wd,
        cfg,
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    outread1 = Path(wd) / "seq" / "input" / "sample1" / "sample1_R1.fq.gz"
    outread2 = Path(wd) / "seq" / "input" / "sample1" / "sample1_R2.fq.gz"
    assert outread1.exists()
    assert outread2.exists()
    subprocess.run(["gzip", "-tv", outread1, outread2])
    captured = capfd.readouterr()
    assert re.search(r"seq/input/sample1/sample1_R1.fq.gz:\s*OK", captured.err)
    assert re.search(r"seq/input/sample1/sample1_R2.fq.gz:\s*OK", captured.err)
