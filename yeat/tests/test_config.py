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
from yeat.cli.config import Assembler, AssemblerConfig, AssemblyConfigurationError, KEYS1, KEYS2
from yeat.tests import data_file


def test_unsupported_assembly_algorithm():
    algorithm = "unsupported_algorithm"
    pattern = rf"Unsupported assembly algorithm '{algorithm}'"
    with pytest.raises(ValueError, match=pattern):
        Assembler("label1", algorithm, ["sample1"])


# check for dupe samples in an assembly run
def test_dupe_samples_in_assembly_run():
    pass


# def test_duplicate_assembly_algorithms():
#     pattern = r"Duplicate assembly configuration: please check config file"
#     with pytest.raises(ValueError, match=pattern):
#         AssemblerConfig.parse_json(open(data_file("dup_algorithms.cfg")))


def test_parse_json():
    f = open(data_file("configs/paired.cfg"))
    samples, algorithms = AssemblerConfig.parse_json(f)
    for sample_name, reads in samples.items():
        assert len(reads.sample) == 2
    assemblers = [assembler.algorithm for assembler in algorithms]
    assert assemblers == ["spades", "megahit", "unicycler"]


def test_valid_config_entry():
    data = json.load(open(data_file("configs/paired.cfg")))
    AssemblerConfig.validate(data, KEYS1)
    for assembler in data["assemblers"]:
        AssemblerConfig.validate(assembler, KEYS2)


@pytest.mark.parametrize("key,", ["label", "algorithm", "extra_args", "samples"])
def test_missing_key_in_config_entry(key):
    data = json.load(open(data_file("configs/paired.cfg")))
    del data["assemblers"][0][key]
    pattern = fr"Missing assembly configuration setting\(s\) '{key}'"
    with pytest.raises(AssemblyConfigurationError, match=pattern):
        AssemblerConfig.validate(data["assemblers"][0], KEYS2)


def test_unsupported_key_in_config_entry():
    data = json.load(open(data_file("configs/paired.cfg")))
    data["assemblers"][0]["not"] = "supported"
    pattern = r"Ignoring unsupported configuration key\(s\) 'not'"
    with pytest.warns(match=pattern):
        AssemblerConfig.validate(data["assemblers"][0], KEYS2)
