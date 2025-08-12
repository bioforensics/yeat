# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from shutil import copy
from pathlib import Path
from pydantic import ValidationError
import pytest
from yeat.config.sample import SampleConfigurationError, Sample
from yeat.tests import data_file


@pytest.mark.parametrize("data", [{}, {"downsample": -1}])
def test_has_one_read_type(data):
    message = "Sample must have at least one read type"
    with pytest.raises(ValidationError, match=message):
        Sample(label="sample1", data=data)


@pytest.mark.parametrize(
    "read_path,expected",
    [
        ("short_reads_?.fastq.gz", ["short_reads_1.fastq.gz", "short_reads_2.fastq.gz"]),
        ("short_reads_1.fastq.gz", ["short_reads_1.fastq.gz"]),
    ],
)
def test_expand_read_path(read_path, expected):
    data = {"illumina": data_file(read_path)}
    Sample._expand_read_path(data)
    assert data["illumina"] == [Path(data_file(read)) for read in expected]


def test_expand_read_path_unable_to_find():
    data = {"illumina": "DNE"}
    message = "Unable to find fastq files"
    with pytest.raises(SampleConfigurationError, match=message):
        Sample._expand_read_path(data)


def test_expand_read_path_found_too_many(tmp_path):
    wd = tmp_path
    read1 = data_file("short_reads_1.fastq.gz")
    read2 = data_file("short_reads_2.fastq.gz")
    copy(read1, wd / "short_reads_1.fastq.gz")
    copy(read2, wd / "short_reads_2.fastq.gz")
    (wd / "short_reads_3.fastq.gz").touch()
    data = {"illumina": str(wd / "short_reads_*.fastq.gz")}
    message = "Found too many fastq files"
    with pytest.raises(SampleConfigurationError, match=message):
        Sample._expand_read_path(data)


@pytest.mark.parametrize(
    "data,read_type",
    [
        ({"illumina": ["DNE"]}, None),
        ({"ont_simplex": ["DNE"]}, "ont_simplex"),
        ({"illumina": ["DNE"], "ont_simplex": ["DNE"]}, "ont_simplex"),
        ({"ont_simplex": ["DNE"], "ont_duplex": ["DNE"]}, "ont_duplex"),
        ({"ont_simplex": ["DNE"], "ont_duplex": ["DNE"]}, "ont_duplex"),
        ({"ont_simplex": ["DNE"], "ont_duplex": ["DNE"], "pacbio_hifi": ["DNE"]}, "pacbio_hifi"),
    ],
)
def test_best_long_read_type(data, read_type):
    sample = Sample(label="sample1", data=data)
    assert sample.best_long_read_type == read_type
