# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pathlib import Path
import pytest
from yeat.config.assemblers.assembler import AssemblerConfigurationError
from yeat.config.assemblers.flye import FlyeAssembler
from yeat.config.assemblers.spades import SPAdesAssembler
from yeat.config.sample import Sample


def test_requested_sample_not_avaliable():
    data = {"algorithm": "spades", "samples": ["sample_DNE"]}
    samples = {"sample1": Sample(label="sample1", data={"illumina": ["read_?.fastq.gz"]})}
    message = "Sample 'sample_DNE' not found in provided samples"
    with pytest.raises(AssemblerConfigurationError, match=message):
        SPAdesAssembler.select_samples(data, samples)


def test_find_all_avaliable_samples():
    data = {"algorithm": "flye"}
    samples = {
        "sample1": Sample(label="sample1", data={"illumina": ["read_?.fastq.gz"]}),
        "sample2": Sample(label="sample2", data={"ont_simplex": ["read.fastq.gz"]}),
    }
    compatible_samples = FlyeAssembler.select_samples(data, samples)
    expected = {"ont_simplex": [Path("read.fastq.gz")]}
    assert compatible_samples["sample2"].data == expected
