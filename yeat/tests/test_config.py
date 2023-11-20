# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import json
import pytest
from unittest.mock import patch
from yeat.config import AssemblyConfigError
from yeat.config.assembly import Assembly
from yeat.config.config import AssemblyConfig
from yeat.config.sample import Sample
from yeat.tests import data_file

pytestmark = pytest.mark.short


def test_invalid_assembly_algorithm():
    label = "assembly_label"
    data = {
        "algorithm": "invalid_assembly_algorithm",
        "extra_args": "",
        "samples": ["sample1"],
        "mode": "paired",
    }
    pattern = rf"Invalid assembly algorithm '{data['algorithm']}' for '{label}'"
    with pytest.raises(ValueError, match=pattern):
        Assembly(label, data, 1)


@patch("yeat.config.assembly.platform", "darwin")
def test_linux_only_algorithm():
    data = {
        "algorithm": "metamdbg",
        "extra_args": "",
        "samples": ["sample1"],
        "mode": "pacbio",
    }
    pattern = r"Assembly algorithm 'metaMDBG' can only run on 'Linux OS'"
    with pytest.raises(ValueError, match=pattern):
        Assembly("assembly_label", data, 1)


def test_valid_config():
    data = json.load(open(data_file("configs/paired.cfg")))
    config = AssemblyConfig(data, 1)
    assert len(config.samples) == 2
    assert len(config.assemblies) == 3


@pytest.mark.parametrize("key,", ["algorithm", "extra_args", "samples", "mode"])
def test_missing_key_in_config_entry(key):
    data = json.load(open(data_file("configs/paired.cfg")))
    del data["assemblies"]["spades-default"][key]
    pattern = rf"Missing assembly configuration setting\(s\) '{key}'"
    with pytest.raises(AssemblyConfigError, match=pattern):
        AssemblyConfig(data, 1)


@pytest.mark.parametrize(
    "reads,badfile",
    [
        (["nonexistant/read1/file", "nonexistant/read2/file"], 0),
        ([data_file("short_reads_1.fastq.gz"), "nonexistant/read2/file"], 1),
        (["nonexistant/read1/file", data_file("short_reads_2.fastq.gz")], 0),
    ],
)
def test_sample_read_file_not_found(reads, badfile):
    label = "sample1"
    data = {"single": reads}
    pattern = rf"No such file '.*{reads[badfile]}' for '{label}'"
    with pytest.raises(FileNotFoundError, match=pattern):
        Sample(label, data)


def test_sample_with_duplicate_reads():
    label = "sample1"
    data = {"paired": [[data_file("short_reads_1.fastq.gz"), data_file("short_reads_1.fastq.gz")]]}
    pattern = rf"Found duplicate read sample '.*short_reads_1.fastq.gz' for '{label}'"
    with pytest.raises(AssemblyConfigError, match=pattern):
        Sample(label, data)


@pytest.mark.parametrize(
    "extra_args,cores,expected",
    [
        ("", 4, r"Missing required extra argument 'genomeSize' for '*'"),
        (
            "genomeSize=4.8m",
            1,
            r"Canu requires at least 4 avaliable cores; increase '-t' or '--threads' to 4 or more",
        ),
    ],
)
def test_check_canu_required_params_errors(extra_args, cores, expected):
    assembler = {
        "algorithm": "canu",
        "extra_args": extra_args,
        "samples": ["sample1"],
        "mode": "pacbio",
    }
    with pytest.raises(ValueError, match=expected):
        Assembly("label1", assembler, cores)
