# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pathlib import Path
from pydantic import ValidationError
import pytest
from yeat.config.config import ConfigurationError, AssemblyConfiguration
from yeat.config.global_settings import GlobalSettings
from yeat.config.sample import Sample


def test_has_one_sample():
    message = "Config has no samples"
    with pytest.raises(ValidationError, match=message):
        AssemblyConfiguration(global_settings=GlobalSettings, samples={}, assemblers={})


def test_has_one_assembler():
    samples = {"sample1": Sample(label="sample1", data={"ont_simplex": [Path("DNE")]})}
    message = "Config has no assemblers"
    with pytest.raises(ValidationError, match=message):
        AssemblyConfiguration(global_settings=GlobalSettings, samples=samples, assemblers={})


def test_algorithm_not_supported():
    message = "Unknown assembly algorithm DNE"
    with pytest.raises(ConfigurationError, match=message):
        AssemblyConfiguration.select("DNE")
