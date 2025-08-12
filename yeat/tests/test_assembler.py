# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pydantic import ValidationError
import pytest
from yeat.config.assemblers.assembler import AssemblerConfigurationError
from yeat.config.assemblers.flye import FlyeAssembler
from yeat.config.sample import Sample


def test_has_one_sample():
    message = "FlyeAssembler has no samples to work with"
    with pytest.raises(ValidationError, match=message):
        FlyeAssembler(label="flye_default", arguments="", samples={})


@pytest.mark.parametrize(
    "data,expected",
    [
        (
            {"algorithm": "flye"},
            {
                "sample2": Sample(label="sample2", data={"ont_simplex": ["read.fastq.gz"]}),
                "sample3": Sample(label="sample3", data={"pacbio_hifi": ["read.fastq.gz"]}),
            },
        ),
        (
            {"algorithm": "flye", "samples": ["sample2"]},
            {"sample2": Sample(label="sample2", data={"ont_simplex": ["read.fastq.gz"]})},
        ),
    ],
)
def test_select_samples(data, expected):
    samples = {
        "sample1": Sample(label="sample1", data={"illumina": ["read.fastq.gz"]}),
        "sample2": Sample(label="sample2", data={"ont_simplex": ["read.fastq.gz"]}),
        "sample3": Sample(label="sample3", data={"pacbio_hifi": ["read.fastq.gz"]}),
    }
    compatible_samples = FlyeAssembler.select_samples(data, samples)
    assert compatible_samples == expected


def test_select_samples_manual_selection_not_avaliable():
    data = {"algorithm": "flye", "samples": ["sample2"]}
    samples = {"sample1": Sample(label="sample1", data={"illumina": ["read.fastq.gz"]})}
    message = "Sample 'sample2' not found in provided samples"
    with pytest.raises(AssemblerConfigurationError, match=message):
        FlyeAssembler.select_samples(data, samples)
