# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
from yeat.config import AssemblerConfig


def test_unsupported_assembly_algorithm():
    algorithm = "unsupported_algorithm"
    pattern = (
        rf"Found unsupported assembly algorithm in configuration settings: \[\[{algorithm}\]\]!"
    )
    with pytest.raises(ValueError, match=pattern):
        AssemblerConfig.check_algorithm(algorithm, [])


def test_duplicate_assembly_algorithms():
    algorithm = "spades"
    pattern = (
        rf"Found duplicate assembly algorithm in configuration settings: \[\[{algorithm}\]\]!"
    )
    with pytest.raises(ValueError, match=pattern):
        AssemblerConfig.check_algorithm(algorithm, ["spades"])
