# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
from yeat.config import AssemblerConfig, AssemblyConfigurationError
from yeat.tests import data_file


def test_unsupported_assembly_algorithm():
    algorithm = "unsupported_algorithm"
    pattern = rf"Unsupported assembly algorithm '{algorithm}'"
    with pytest.raises(ValueError, match=pattern):
        AssemblerConfig(algorithm)


def test_duplicate_assembly_algorithms():
    pattern = r"Duplicate assembly configuration: please check config file"
    with pytest.raises(ValueError, match=pattern):
        AssemblerConfig.parse_json(open(data_file("dup_algorithms.cfg")))


def test_parse_json():
    f = open(data_file("config.cfg"))
    assemblers = [x.algorithm for x in AssemblerConfig.parse_json(f)]
    assert assemblers == ["spades", "megahit"]


def test_valid_config_entry():
    data = {"algorithm": "spades", "extra_args": ""}
    AssemblerConfig.validate(data)


def test_missing_key_in_config_entry():
    data = {"extra_args": ""}
    pattern = r"Missing assembly configuration setting\(s\) 'algorithm'"
    with pytest.raises(AssemblyConfigurationError, match=pattern):
        AssemblerConfig.validate(data)


def test_unsupported_key_in_config_entry():
    data = {"algorithm": "spades", "extra_args": "", "not": "supported"}
    pattern = r"Ignoring unsupported configuration key\(s\) 'not'"
    with pytest.warns(match=pattern):
        AssemblerConfig.validate(data)
