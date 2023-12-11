# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import json
import numpy
from pathlib import Path
import pytest
import subprocess
from unittest.mock import patch
from yeat.config.config import AssemblyConfig
from yeat.tests import data_file
from yeat.workflow import aux

pytestmark = pytest.mark.short


@patch("glob.glob")
@pytest.mark.parametrize(
    "filenames,num_expected",
    [
        ([], 0),
        (["k29.contigs.fa"], 1),
        (["k29.contigs.fa", "not.k.contig.fa"], 1),
        (["k29.contigs.fa", "k39.contigs.fa"], 2),
    ],
)
def test_get_and_filter_contig_files(function_mock, filenames, num_expected):
    sample = "sample1"
    readtype = "single"
    label = "megahit-default"
    path = f"analysis/{sample}/{readtype}/{label}/megahit/intermediate_contigs"
    function_mock.return_value = [f"{path}/{filename}" for filename in filenames]
    fa_files = aux.get_and_filter_contig_files(sample, readtype, label)
    assert len(list(fa_files)) == num_expected


@pytest.mark.parametrize(
    "readtype,flag",
    [("pacbio-raw", "-pacbio"), ("pacbio-corr", "-pacbio"), ("pacbio-hifi", "-pacbio-hifi")],
)
def test_get_canu_readtype_flag(readtype, flag):
    assert aux.get_canu_readtype_flag(readtype) == flag


@pytest.mark.parametrize("compressed", [(True), (False)])
def test_combine(compressed, tmp_path):
    wd = str(tmp_path)
    outdir = Path(wd) / "input/sample1"
    outdir.mkdir(parents=True)
    if compressed:
        reads = [data_file("short_reads_1.fastq.gz")]
    else:
        inread = data_file("short_reads_1.fastq.gz")
        outread = str(outdir / "short_reads_1.fastq")
        subprocess.run(f"gunzip -c {inread} > {outread}", shell=True)
        reads = [outread]
    direction = "r1"
    aux.combine(reads, direction, outdir)
    assert (outdir / f"{direction}_combined-reads.fq.gz").exists()


@pytest.mark.parametrize("input", [(0), (numpy.int64(6275000))])
def test_get_genome_size(input):
    genome_size = aux.get_genome_size(input, data_file("combined-reads.report.tsv"))
    assert isinstance(genome_size, numpy.integer)
    assert genome_size > 0
    if input != 0:
        assert genome_size == input


def test_get_avg_read_length():
    avg_read_length = aux.get_avg_read_length(data_file("fastp.json"))
    assert avg_read_length == 125.0


@pytest.mark.parametrize("downsample", [(0), (3765000)])
def test_get_down(downsample):
    genome_size = 6275000
    coverage = 150
    avg_read_length = 125.0
    down = aux.get_down(downsample, genome_size, coverage, avg_read_length)
    assert isinstance(down, int)
    assert down >= 0
    if downsample != 0:
        assert down == downsample


@pytest.mark.parametrize("input", [("None"), (81)])
def test_get_seed(input):
    seed = aux.get_seed(input)
    assert isinstance(seed, int)
    assert seed > 0
    if input != "None":
        assert seed == input


def test_print_downsample_values(capsys):
    genome_size = 6275000
    avg_read_length = 125.0
    coverage = 150
    down = 3765000
    seed = 802
    aux.print_downsample_values(genome_size, avg_read_length, coverage, down, seed)
    captured = capsys.readouterr()
    expected = (
        f"[yeat] genome size: {genome_size}\n"
        f"[yeat] average read length: {avg_read_length}\n"
        f"[yeat] target depth of coverage: {coverage}x\n"
        f"[yeat] number of reads to sample: {down}\n"
        f"[yeat] random seed for sampling: {seed}\n"
    )
    assert captured.out == expected


def test_get_expected_files():
    data = json.load(open(data_file("configs/example.cfg")))
    cfg = AssemblyConfig(data, 4)
    config = {"samples": cfg.samples, "assemblies": cfg.assemblies}
    observed = aux.get_expected_files(config)
    expected = [
        "analysis/sample1/paired/spades-default/spades/bandage/.done",
        "seq/fastqc/sample1/paired/r1_combined-reads_fastqc.html",
        "seq/fastqc/sample1/paired/r2_combined-reads_fastqc.html",
        "analysis/sample2/paired/spades-default/spades/bandage/.done",
        "seq/fastqc/sample2/paired/r1_combined-reads_fastqc.html",
        "seq/fastqc/sample2/paired/r2_combined-reads_fastqc.html",
        "analysis/sample3/pacbio-hifi/hicanu/canu/bandage/.done",
        "seq/fastqc/sample3/pacbio-hifi/combined-reads_fastqc.html",
        "analysis/sample4/nano-hq/flye_ONT/flye/bandage/.done",
        "seq/nanoplot/sample4/nano-hq/raw_LengthvsQualityScatterPlot_dot.pdf",
        "seq/nanoplot/sample4/nano-hq/filtered_LengthvsQualityScatterPlot_dot.pdf",
    ]
    assert observed == expected


@pytest.mark.parametrize(
    "run_bandage,file",
    [(True, "bandage/.done"), (False, "quast/report.html")],
)
def test_get_file(run_bandage, file):
    sample = "sample1"
    readtype = "single"
    assembly = "spades-default"
    algorithm = "spades"
    observed = aux.get_file(run_bandage, sample, readtype, assembly, algorithm)
    expected = f"analysis/{sample}/{readtype}/{assembly}/{algorithm}/{file}"
    assert observed == expected
