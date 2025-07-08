# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import json
import pytest
from unittest.mock import patch
from yeat.config import AssemblyConfigError
from yeat.config.assemblers.assembler import Assembly
from yeat.config.sample import Sample
from yeat.tests import data_file

pytestmark = pytest.mark.short


def test_invalid_assembly_algorithm():
    config_data = json.load(open(data_file("configs/example.cfg")))
    samples = {"sample1": Sample("sample1", config_data["samples"]["sample1"])}
    assembly_label = "label1"
    assembly_data = {
        "algorithm": "INVALID",
        "extra_args": "",
        "samples": samples,
        "mode": "paired",
    }
    pattern = rf"Invalid assembly algorithm '{assembly_data['algorithm']}' for '{assembly_label}'"
    with pytest.raises(ValueError, match=pattern):
        Assembly(assembly_label, assembly_data)


@patch("yeat.config.assembly.platform", "darwin")
def test_linux_only_algorithm():
    config_data = json.load(open(data_file("configs/example.cfg")))
    samples = {"sample3", Sample("sample3", config_data["samples"]["sample3"])}
    assembly_data = {
        "algorithm": "metamdbg",
        "extra_args": "",
        "samples": samples,
        "mode": "pacbio",
    }
    pattern = r"Assembly algorithm 'metaMDBG' can only run on 'Linux OS'"
    with pytest.raises(ValueError, match=pattern):
        Assembly("label1", assembly_data)


@pytest.mark.parametrize(
    "extra_args,cores,expected",
    [
        ("", 4, r"Missing required extra argument 'genomeSize' for '*'"),
        (
            "genomeSize=4.8m",
            1,
            r"Canu requires at least 4 avaliable cores; increase '-t' or '--threads' to 4 or more",
        ),
    ],
)
def test_check_canu_required_params_errors(extra_args, cores, expected):
    config_data = json.load(open(data_file("configs/example.cfg")))
    samples = {"sample3": Sample("sample3", config_data["samples"]["sample3"])}
    assembly_data = {
        "algorithm": "canu",
        "extra_args": extra_args,
        "samples": samples,
        "mode": "pacbio",
    }
    with pytest.raises(ValueError, match=expected):
        Assembly("label1", assembly_data, cores)


def test_check_valid_mode():
    config_data = json.load(open(data_file("configs/example.cfg")))
    samples = {"sample1": Sample("sample1", config_data["samples"]["sample1"])}
    assembly_label = "label1"
    assembly_data = {
        "algorithm": "spades",
        "extra_args": "",
        "samples": samples,
        "mode": "INVALID",
    }
    pattern = rf"Invalid assembly mode '{assembly_data['mode']}' for '{assembly_label}'"
    with pytest.raises(AssemblyConfigError, match=pattern):
        Assembly(assembly_label, assembly_data)
