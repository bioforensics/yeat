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

pytestmark = pytest.mark.short


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
