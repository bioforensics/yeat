# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import SAMPLES
from copy import deepcopy
import pytest
from yeat.config.assemblers.assembler import AssemblerConfigurationError
from yeat.config.assemblers.flye import FlyeAssembler
from yeat.config.assemblers.spades import SPAdesAssembler


@pytest.mark.parametrize("samples", [{"sample1": SAMPLES["sample1"]}, SAMPLES])
def test_has_one_sample(samples):
    SPAdesAssembler.has_one_sample(samples)


def test_has_no_sample():
    message = "Assembler has no samples to work with"
    with pytest.raises(AssemblerConfigurationError, match=message):
        SPAdesAssembler.has_one_sample(samples={})


def test_parse_data():
    label = "spades_default"
    data = {"algorithm": "spades"}
    samples = {"sample1": SAMPLES["sample1"]}
    SPAdesAssembler.parse_data(label, data, samples)


@pytest.mark.parametrize(
    "data,expected",
    [
        ({"algorithm": "flye"}, ["sample3", "sample4"]),
        ({"algorithm": "flye", "samples": ["sample3"]}, ["sample3"]),
    ],
)
def test_select_samples(data, expected):
    compatible_samples = FlyeAssembler.select_samples(data, SAMPLES)
    assert list(compatible_samples.keys()) == expected


def test_incompatiable_sample_selected():
    data = {"algorithm": "flye", "samples": ["sample1"]}
    compatible_samples = FlyeAssembler.select_samples(data, SAMPLES)
    assert compatible_samples == {}


def test_no_compatible_sample_avaliable():
    data = {"algorithm": "flye"}
    samples = deepcopy(SAMPLES)
    del samples["sample3"]
    del samples["sample4"]
    compatible_samples = FlyeAssembler.select_samples(data, samples)
    assert compatible_samples == {}


def test_select_samples_manual_selection_not_avaliable():
    data = {"algorithm": "flye", "samples": ["sample5"]}
    message = "Sample 'sample5' not found in provided samples"
    with pytest.raises(AssemblerConfigurationError, match=message):
        FlyeAssembler.select_samples(data, SAMPLES)


@pytest.mark.parametrize(
    "data,expected",
    [
        ({"algorithm": "spades"}, ""),
        ({"algorithm": "spades", "arguments": "--isolate"}, "--isolate"),
    ],
)
def test_extra_args(data, expected):
    label = "spades_default"
    samples = {"sample1": SAMPLES["sample1"]}
    assembler = SPAdesAssembler.parse_data(label, data, samples)
    assert assembler.extra_args == expected
