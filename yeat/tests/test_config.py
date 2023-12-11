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
    label = "label1"
    data = {
        "algorithm": "INVALID",
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
        Assembly("label1", data, 1)


def test_valid_config():
    data = json.load(open(data_file("configs/example.cfg")))
    config = AssemblyConfig(data, 4)
    assert len(config.samples) == 4
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
    data = {
        "algorithm": "canu",
        "extra_args": extra_args,
        "samples": ["sample1"],
        "mode": "pacbio",
    }
    with pytest.raises(ValueError, match=expected):
        Assembly("label1", data, cores)


def test_check_valid_mode():
    label = "label1"
    data = {
        "algorithm": "spades",
        "extra_args": "",
        "samples": ["sample1"],
        "mode": "INVALID",
    }
    pattern = rf"Invalid assembly mode '{data['mode']}' for '{label}'"
    with pytest.raises(AssemblyConfigError, match=pattern):
        Assembly(label, data, 1)


@pytest.mark.parametrize("layer", ["base", "sample", "assembly"])
def test_check_valid_keys(layer):
    data = json.load(open(data_file("configs/paired.cfg")))
    if layer == "base":
        data["INVALID1"] = ""
        data["INVALID2"] = ""
    elif layer == "sample":
        data["samples"]["Shigella_sonnei_53G"]["INVALID1"] = ""
        data["samples"]["Shigella_sonnei_53G"]["INVALID2"] = ""
    elif layer == "assembly":
        data["assemblies"]["spades-default"]["INVALID1"] = ""
        data["assemblies"]["spades-default"]["INVALID2"] = ""
    pattern = r"Found unsupported configuration key\(s\) 'INVALID1,INVALID2'"
    with pytest.raises(AssemblyConfigError, match=pattern):
        AssemblyConfig(data, 1)


@pytest.mark.parametrize(
    "mode,label", [("paired", "spades-default"), ("pacbio", "hicanu"), ("oxford", "flye_ONT")]
)
def test_validate_samples_to_assembly_modes(mode, label):
    data = json.load(open(data_file("configs/example.cfg")))
    if mode == "paired":
        data["assemblies"]["spades-default"]["samples"] = ["sample4"]
    elif mode == "pacbio":
        data["assemblies"]["hicanu"]["samples"] = ["sample1"]
    elif mode == "oxford":
        data["assemblies"]["flye_ONT"]["samples"] = ["sample1"]
    pattern = rf"No samples can interact with assembly mode '{mode}' for '{label}'"
    with pytest.raises(AssemblyConfigError, match=pattern):
        AssemblyConfig(data, 4)


@pytest.mark.parametrize(
    "test,pattern",
    [
        ("no_reads", r"Missing sample reads for 'sample1'"),
        ("too_many_reads", r"Max of 2 readtypes per sample for 'sample1'"),
        ("too_many_shorttypes", r"Max of 1 Illumina readtype per sample for 'sample1'"),
        ("too_many_longtypes", r"Max of 1 long readtype per sample for 'sample1'"),
    ],
)
def test_check_one_readtype_limit(test, pattern):
    if test == "no_reads":
        data = {}
    elif test == "too_many_reads":
        data = {
            "paired": [[data_file("Animal_289_R1.fq.gz"), data_file("Animal_289_R2.fq.gz")]],
            "single": [data_file("short_reads_1.fastq.gz")],
            "pacbio-hifi": [data_file("ecoli.fastq.gz")],
        }
    elif test == "too_many_shorttypes":
        data = {
            "paired": [[data_file("Animal_289_R1.fq.gz"), data_file("Animal_289_R2.fq.gz")]],
            "single": [data_file("short_reads_1.fastq.gz")],
        }
    elif test == "too_many_longtypes":
        data = {
            "pacbio-hifi": [data_file("ecoli.fastq.gz")],
            "nano-hq": [data_file("ecolk12mg1655_R10_3_guppy_345_HAC.fastq.gz")],
        }
    with pytest.raises(AssemblyConfigError, match=pattern):
        Sample("sample1", data)


def test_check_input_reads():
    label = "sample1"
    data = {"paired": []}
    pattern = rf"Missing input reads for '{label}'"
    with pytest.raises(AssemblyConfigError, match=pattern):
        Sample(label, data)


@pytest.mark.parametrize(
    "test,pattern",
    [
        ("not_list_1", r"Input read is not a list 'INVALID' for 'sample1'"),
        ("not_list_2", r"Input read is not a list 'INVALID' for 'sample1'"),
        ("missing_one_pair", r"Missing 2 reads in 'paired' entry for 'sample1'"),
        ("missing_both_pairs", r"Missing 1 read in 'paired' entry for 'sample1'"),
        ("too_many_pairs", r"Found more than 2 reads in 'paired' entry for 'sample1'"),
    ],
)
def test_check_paired_reads(test, pattern):
    if test == "not_list_1":
        data = {"paired": ["INVALID"]}
    elif test == "not_list_2":
        data = {
            "paired": [
                [data_file("Animal_289_R1.fq.gz"), data_file("Animal_289_R2.fq.gz")],
                "INVALID",
            ]
        }
    elif test == "missing_one_pair":
        data = {"paired": [[]]}
    elif test == "missing_both_pairs":
        data = {"paired": [[data_file("Animal_289_R1.fq.gz")]]}
    elif test == "too_many_pairs":
        data = {
            "paired": [
                [
                    data_file("Animal_289_R1.fq.gz"),
                    data_file("Animal_289_R2.fq.gz"),
                    data_file("short_reads_1.fastq.gz"),
                ]
            ]
        }
    with pytest.raises(AssemblyConfigError, match=pattern):
        Sample("sample1", data)


@pytest.mark.parametrize("test", ["flat_list", "nested_lists"])
def test_check_reads(test):
    label = "sample1"
    if test == "flat_list":
        data = {"single": [[]]}
    elif test == "nested_lists":
        data = {"paired": [[data_file("Animal_289_R1.fq.gz"), []]]}
    pattern = rf"Input read is not a string '\[\]' for '{label}'"
    with pytest.raises(AssemblyConfigError, match=pattern):
        Sample(label, data)
