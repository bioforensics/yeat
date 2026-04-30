# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import SAMPLES
from collections import Counter
from glob import glob
from shutil import copy
import pytest
from yeat.config.global_settings import GlobalSettings
from yeat.config.sample import SampleConfigurationError, Sample
from yeat.tests import data_file


def test_has_one_read_type():
    data = {"illumina": ["READ1.fastq.gz", "READ2.fastq.gz"]}
    Sample.has_one_read_type(data)


def test_has_no_read_type():
    message = "Sample must have at least one read type"
    with pytest.raises(SampleConfigurationError, match=message):
        Sample.has_one_read_type({})


@pytest.mark.parametrize(
    "read_path",
    [
        [data_file("short_reads_1.fastq.gz"), data_file("short_reads_2.fastq.gz")],
        [data_file("short_reads_1.fastq.gz")],
    ],
)
def test_has_read_paths(read_path):
    data = {"illumina": read_path}
    Sample.has_read_paths(data)


def test_has_read_paths_add_global_setting_keys():
    data = {"illumina": ["READ1.fastq.gz", "READ2.fastq.gz"], "filter": {"enabled": False}}
    Sample.has_read_paths(data)


def test_has_read_paths_unable_to_find():
    data = {"illumina": []}
    message = "Unable to find FASTQ files for sample"
    with pytest.raises(SampleConfigurationError, match=message):
        Sample.has_read_paths(data)


def test_has_read_paths_found_too_many(tmp_path):
    wd = tmp_path
    read1 = data_file("short_reads_1.fastq.gz")
    read2 = data_file("short_reads_2.fastq.gz")
    copy(read1, wd / "short_reads_1.fastq.gz")
    copy(read2, wd / "short_reads_2.fastq.gz")
    (wd / "short_reads_3.fastq.gz").touch()
    data = {"illumina": glob(str(wd / "short_reads_*.fastq.gz"))}
    message = "Sample has too many FASTQ files. Expected at most 2, found 3."
    with pytest.raises(SampleConfigurationError, match=message):
        Sample.has_read_paths(data)


def test_has_invalid_keys():
    message = r"Sample has unexpected key\(s\): \{'INVALID'\}"
    with pytest.raises(SampleConfigurationError, match=message):
        Sample.has_invalid_keys({"INVALID": "INVALID"})


@pytest.mark.parametrize(
    "data",
    [
        {"illumina": ["READ1.fastq.gz", "READ2.fastq.gz"]},
        {"illumina": ["READ.fastq.gz"]},
        {"pacbio_hifi": ["READ.fastq.gz"]},
        {"ont_duplex": ["READ.fastq.gz"]},
        {"ont_simplex": ["READ.fastq.gz"]},
        {"ont_ultralong": ["READ.fastq.gz"]},
    ],
)
def test_has_valid_keys(data):
    Sample.has_invalid_keys(data)


def test_parse_data():
    data = {"illumina": ["READ1.fastq.gz", "READ2.fastq.gz"]}
    global_settings = GlobalSettings(filter={}, downsample={})
    Sample.parse_data("sample1", data, global_settings)


@pytest.mark.parametrize(
    "data,read_type",
    [
        ({"illumina": ["READ.fastq.gz"]}, None),
        ({"ont_simplex": ["READ.fastq.gz"]}, "ont_simplex"),
        ({"illumina": ["READ.fastq.gz"], "ont_simplex": ["READ.fastq.gz"]}, "ont_simplex"),
        ({"ont_simplex": ["READ.fastq.gz"], "ont_duplex": ["READ.fastq.gz"]}, "ont_duplex"),
        ({"ont_simplex": ["READ.fastq.gz"], "ont_duplex": ["READ.fastq.gz"]}, "ont_duplex"),
        (
            {
                "ont_simplex": ["READ.fastq.gz"],
                "ont_duplex": ["READ.fastq.gz"],
                "pacbio_hifi": ["READ.fastq.gz"],
            },
            "pacbio_hifi",
        ),
    ],
)
def test_best_long_read_type(data, read_type):
    sample = Sample(label="sample1", data=data)
    assert sample.best_long_read_type == read_type


def test_sample_settings():
    sample = SAMPLES["sample1"]
    assert sample.filter_enabled("short") == False
    assert sample.filter_args("short") == "--min-length 50 --detect_adapter_for_pe"
    assert sample.downsample_enabled("short") == False
    assert sample.downsample_method("short") == "random"
    assert sample.target_depth("short") == 150
    assert sample.target_num_reads("short") == "auto"
    assert sample.genome_size("short") == "auto"


def test_targets():
    data = {"illumina": ["READ1.fastq.gz", "READ2.fastq.gz"], "ont_simplex": ["READ.fastq.gz"]}
    sample = Sample(label="sample1", data=data)
    assert Counter(sample.targets) == Counter(
        [
            "analysis/sample1/qc/illumina/fastqc/R1_fastqc.html",
            "analysis/sample1/qc/illumina/fastqc/R2_fastqc.html",
            "analysis/sample1/qc/ont_simplex/fastqc/read_fastqc.html",
        ]
    )
