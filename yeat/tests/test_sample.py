# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from shutil import copy
from pydantic import ValidationError
import pytest
from yeat.config.sample import SampleConfigurationError, Sample
from yeat.tests import data_file


@pytest.mark.parametrize("data", [{}, {"target_num_reads": -1}])
def test_has_one_read_type(data):
    message = "Sample must have at least one read type"
    with pytest.raises(ValidationError, match=message):
        Sample(label="sample1", data=data)


def test_has_valid_keys():
    data = {"illumina": [data_file("short_reads_1.fastq.gz")], "INVALID": 0}
    message = r"Sample has unexpected key\(s\): \{'INVALID'\}"
    with pytest.raises(ValidationError, match=message):
        Sample(label="sample1", data=data)


@pytest.mark.parametrize(
    "read_path",
    [
        [data_file("short_reads_1.fastq.gz"), data_file("short_reads_2.fastq.gz")],
        [data_file("short_reads_1.fastq.gz")],
    ],
)
def test_check_read_paths(read_path):
    label = "sample1"
    data = {"illumina": read_path}
    Sample._check_read_paths(label, data)


def test_check_read_paths_unable_to_find():
    label = "sample1"
    data = {"illumina": []}
    message = f"Unable to find FASTQ files for sample '{label}' at path:"
    with pytest.raises(SampleConfigurationError, match=message):
        Sample._check_read_paths(label, data)


def test_check_read_paths_found_too_many(tmp_path):
    wd = tmp_path
    read1 = data_file("short_reads_1.fastq.gz")
    read2 = data_file("short_reads_2.fastq.gz")
    copy(read1, wd / "short_reads_1.fastq.gz")
    copy(read2, wd / "short_reads_2.fastq.gz")
    (wd / "short_reads_3.fastq.gz").touch()
    label = "sample1"
    data = {"illumina": str(wd / "short_reads_*.fastq.gz")}
    message = f"Found too many FASTQ files for sample '{label}' at path:"
    with pytest.raises(SampleConfigurationError, match=message):
        Sample._check_read_paths(label, data)


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
