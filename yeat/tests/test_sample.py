# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
from yeat.config import AssemblyConfigError
from yeat.config.sample import Sample
from yeat.tests import data_file

pytestmark = pytest.mark.short


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
    data = {"single": reads, "downsample": 0, "genome_size": 0, "coverage_depth": 150}
    pattern = rf"No such file '.*{reads[badfile]}' for '{label}'"
    with pytest.raises(FileNotFoundError, match=pattern):
        Sample(label, data)


def test_sample_with_duplicate_reads():
    label = "sample1"
    data = {
        "paired": [[data_file("short_reads_1.fastq.gz"), data_file("short_reads_1.fastq.gz")]],
        "downsample": 0,
        "genome_size": 0,
        "coverage_depth": 150,
    }
    pattern = rf"Found duplicate read sample '.*short_reads_1.fastq.gz' for '{label}'"
    with pytest.raises(AssemblyConfigError, match=pattern):
        Sample(label, data)


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
        data = {"downsample": 0, "genome_size": 0, "coverage_depth": 150}
    elif test == "too_many_reads":
        data = {
            "paired": [[data_file("Animal_289_R1.fq.gz"), data_file("Animal_289_R2.fq.gz")]],
            "single": [data_file("short_reads_1.fastq.gz")],
            "pacbio-hifi": [data_file("ecoli.fastq.gz")],
            "downsample": 0,
            "genome_size": 0,
            "coverage_depth": 150,
        }
    elif test == "too_many_shorttypes":
        data = {
            "paired": [[data_file("Animal_289_R1.fq.gz"), data_file("Animal_289_R2.fq.gz")]],
            "single": [data_file("short_reads_1.fastq.gz")],
            "downsample": 0,
            "genome_size": 0,
            "coverage_depth": 150,
        }
    elif test == "too_many_longtypes":
        data = {
            "pacbio-hifi": [data_file("ecoli.fastq.gz")],
            "nano-hq": [data_file("ecolk12mg1655_R10_3_guppy_345_HAC.fastq.gz")],
            "downsample": 0,
            "genome_size": 0,
            "coverage_depth": 150,
        }
    with pytest.raises(AssemblyConfigError, match=pattern):
        Sample("sample1", data)


def test_check_input_reads():
    label = "sample1"
    data = {"paired": [], "downsample": 0, "genome_size": 0, "coverage_depth": 150}
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
        data = {"paired": ["INVALID"], "downsample": 0, "genome_size": 0, "coverage_depth": 150}
    elif test == "not_list_2":
        data = {
            "paired": [
                [data_file("Animal_289_R1.fq.gz"), data_file("Animal_289_R2.fq.gz")],
                "INVALID",
            ],
            "downsample": 0,
            "genome_size": 0,
            "coverage_depth": 150,
        }
    elif test == "missing_one_pair":
        data = {"paired": [[]], "downsample": 0, "genome_size": 0, "coverage_depth": 150}
    elif test == "missing_both_pairs":
        data = {
            "paired": [[data_file("Animal_289_R1.fq.gz")]],
            "downsample": 0,
            "genome_size": 0,
            "coverage_depth": 150,
        }
    elif test == "too_many_pairs":
        data = {
            "paired": [
                [
                    data_file("Animal_289_R1.fq.gz"),
                    data_file("Animal_289_R2.fq.gz"),
                    data_file("short_reads_1.fastq.gz"),
                ]
            ],
            "downsample": 0,
            "genome_size": 0,
            "coverage_depth": 150,
        }
    with pytest.raises(AssemblyConfigError, match=pattern):
        Sample("sample1", data)


@pytest.mark.parametrize("test", ["flat_list", "nested_lists"])
def test_check_reads(test):
    label = "sample1"
    if test == "flat_list":
        data = {"single": [[]], "downsample": 0, "genome_size": 0, "coverage_depth": 150}
    elif test == "nested_lists":
        data = {
            "paired": [[data_file("Animal_289_R1.fq.gz"), []]],
            "downsample": 0,
            "genome_size": 0,
            "coverage_depth": 150,
        }
    pattern = rf"Input read is not a string '\[\]' for '{label}'"
    with pytest.raises(AssemblyConfigError, match=pattern):
        Sample(label, data)


@pytest.mark.parametrize("key", [("downsample"), ("genome_size"), ("coverage_depth")])
def test_cannot_cast_downsample_values_to_int(key):
    data = {
        "paired": [
            ["yeat/tests/data/short_reads_1.fastq.gz", "yeat/tests/data/short_reads_2.fastq.gz"]
        ],
        "downsample": 0,
        "genome_size": 0,
        "coverage_depth": 150,
    }
    data[key] = "BAD"
    message = f"Input {key} is not an int 'BAD' for 'sample1'"
    with pytest.raises(ValueError, match=message):
        Sample("sample1", data)


@pytest.mark.parametrize(
    "key,value", [("downsample", -2), ("genome_size", -1), ("coverage_depth", 0)]
)
def test_check_input_downsample_values(key, value):
    data = {
        "paired": [
            ["yeat/tests/data/short_reads_1.fastq.gz", "yeat/tests/data/short_reads_2.fastq.gz"]
        ],
        "downsample": 0,
        "genome_size": 0,
        "coverage_depth": 150,
    }
    data[key] = value
    message = f"Invalid input '{value}' for 'sample1'"
    with pytest.raises(AssemblyConfigError, match=message):
        Sample("sample1", data)


@pytest.mark.parametrize("key", [("downsample"), ("genome_size"), ("coverage_depth")])
def test_warn_downsample_configuration_on_long_reads(key):
    data = {
        "pacbio-corr": ["yeat/tests/data/long_reads_high_depth.fastq.gz"],
        "downsample": 0,
        "genome_size": 0,
        "coverage_depth": 150,
    }
    data[key] = 10000
    message = f"Configuration value '{key}' cannot be applied to 'pacbio-corr'"
    with pytest.warns(UserWarning, match=message):
        Sample("sample1", data)
