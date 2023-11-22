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
from yeat.tests import *


@pytest.mark.short
def test_paired_end_assemblers_dry_run(tmp_path):
    wd = str(tmp_path)
    arglist = ["-o", wd, "-n", data_file("configs/paired.cfg")]
    run_yeat(arglist)


@pytest.mark.long
@pytest.mark.illumina
@pytest.mark.parametrize("algorithm", ["spades", "megahit", "unicycler"])
def test_paired_end_assemblers(algorithm, capsys, tmp_path):
    wd = str(tmp_path)
    config, data = write_config(algorithm, wd, "paired.cfg")
    arglist = ["-o", wd, config]
    run_yeat(arglist)
    expected = get_expected(algorithm, wd, data)
    files_exist(expected)


@pytest.mark.long
@pytest.mark.illumina
def test_multiple_paired_end_assemblers(capsys, tmp_path):
    wd = str(tmp_path)
    arglist = ["-o", wd, data_file(f"configs/paired.cfg")]
    run_yeat(arglist)
    outdirs = {
        "sample1": Path(wd).resolve() / "analysis" / "sample1" / "paired",
        "sample2": Path(wd).resolve() / "analysis" / "sample2" / "paired",
    }
    for sample, outdir in outdirs.items():
        assert (outdir / "spades-default" / "spades" / "contigs.fasta").exists()
        assert (outdir / "megahit-default" / "megahit" / "final.contigs.fa").exists()
        assert (outdir / "unicycler-default" / "unicycler" / "assembly.fasta").exists()


@pytest.mark.long
@pytest.mark.illumina
def test_multiple_spades(capsys, tmp_path):
    wd = str(tmp_path)
    arglist = ["-o", wd, data_file(f"configs/two_spades.cfg")]
    run_yeat(arglist)
    paired_dir = Path(wd).resolve() / "analysis" / "sample1" / "paired"
    assert (paired_dir / "spades-default" / "spades" / "contigs.fasta").exists()
    assert (paired_dir / "spades-meta" / "spades" / "contigs.fasta").exists()


@pytest.mark.long
@pytest.mark.illumina
@pytest.mark.parametrize(
    "downsample,num_contigs,largest_contig,total_len",
    [("2000", 79, 5294, 70818), ("-1", 56, 35168, 199940)],
)
def test_custom_downsample_input(
    downsample, num_contigs, largest_contig, total_len, capsys, tmp_path
):
    wd = str(tmp_path)
    arglist = ["-o", wd, "-d", downsample, "--seed", "0", data_file("configs/megahit.cfg")]
    run_yeat(arglist)
    paired_dir = Path(wd).resolve() / "analysis" / "sample1" / "paired"
    quast_report = paired_dir / "megahit-default" / "megahit" / "quast" / "report.tsv"
    df = pd.read_csv(quast_report, sep="\t")
    assert df.iloc[12]["contigs"] == num_contigs
    assert df.iloc[13]["contigs"] == largest_contig
    assert df.iloc[14]["contigs"] == total_len


@pytest.mark.long
@pytest.mark.illumina
@pytest.mark.parametrize("coverage", [("150"), ("75"), ("10")])
def test_custom_coverage_input(coverage, capsys, tmp_path):
    wd = str(tmp_path)
    arglist = ["-o", wd, "-c", coverage, data_file("configs/megahit.cfg")]
    run_yeat(arglist)
    paired_dir = Path(wd).resolve() / "analysis" / "sample1" / "paired"
    quast_report = paired_dir / "megahit-default" / "megahit" / "quast" / "report.tsv"
    df = pd.read_csv(quast_report, sep="\t")
    num_contigs = df.iloc[12]["contigs"]
    assert num_contigs == 56
    largest_contig = df.iloc[13]["contigs"]
    assert largest_contig == 35168
    total_len = df.iloc[14]["contigs"]
    assert total_len == 199940


@pytest.mark.long
@pytest.mark.illumina
@pytest.mark.parametrize("execution_number", range(3))
def test_random_downsample_seed(execution_number, capsys, tmp_path):
    wd = str(tmp_path)
    arglist = ["-o", wd, "-d", "2000", data_file("configs/megahit.cfg")]
    run_yeat(arglist)
    paired_dir = Path(wd).resolve() / "analysis" / "sample1" / "paired"
    quast_report = paired_dir / "megahit-default" / "megahit" / "quast" / "report.tsv"
    df = pd.read_csv(quast_report, sep="\t")
    num_contigs = df.iloc[12]["contigs"]
    assert num_contigs == pytest.approx(76, abs=15)  # 76 +/- 20%
    largest_contig = df.iloc[13]["contigs"]
    assert largest_contig == pytest.approx(5228, abs=1045)  # 5228 +/- 20%
    total_len = df.iloc[14]["contigs"]
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
@pytest.mark.illumina
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
    cfg_data["samples"]["sample1"] = {"paired": [[inread1, inread2]]}
    cfg = str(Path(wd).resolve() / "megahit.cfg")
    json.dump(cfg_data, open(cfg, "w"))
    arglist = ["-o", wd, cfg]
    run_yeat(arglist)
    outdir = Path(wd) / "seq" / "input" / "sample1" / "paired"
    uncomp_read1 = outdir / "r1_reads0.fq"
    uncomp_read2 = outdir / "r2_reads0.fq"
    assert uncomp_read1.exists()
    assert uncomp_read2.exists()
    outread1 = outdir / "r1_combined-reads.fq.gz"
    outread2 = outdir / "r2_combined-reads.fq.gz"
    subprocess.run(["gzip", "-tv", outread1, outread2])
    captured = capfd.readouterr()
    assert re.search(r"seq/input/sample1/paired/r1_combined-reads.fq.gz:\s*OK", captured.err)
    assert re.search(r"seq/input/sample1/paired/r2_combined-reads.fq.gz:\s*OK", captured.err)
