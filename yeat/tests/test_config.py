# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
from yeat.config.config import ConfigurationError, AssemblyConfiguration
from yeat.config.global_settings import GlobalSettings


def test_algorithm_not_supported():
    message = "unknown assembly algorithm algorithm_DNE"
    with pytest.raises(ConfigurationError, match=message):
        AssemblyConfiguration.select("algorithm_DNE")
