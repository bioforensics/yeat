# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from distutils.log import error
import io
import json
from yeat.assembly import config
import pytest


def test_unsupported_assembly_algorithm():
    data = [{"label": "assembly1", "algorithm": "unsupported_assembly"}]
    f = io.StringIO(json.dumps(data))
    error_message = (
        r"Found unsupported assembly algorithm in config file: \[\[unsupported_assembly\]\]!"
    )
    with pytest.raises(config.AssemblyConfigError, match=error_message):
        config.AssemblyConfiguration.parse_json(f)


def test_duplicate_assembly_algorithms():
    data = [
        {"label": "assembly1", "algorithm": "spades"},
        {"label": "assembly2", "algorithm": "spades"},
    ]
    f = io.StringIO(json.dumps(data))
    error_message = r"Found duplicate assembly algorithm found in config file: \[\[spades\]\]!"
    with pytest.raises(config.AssemblyConfigError, match=error_message):
        config.AssemblyConfiguration.parse_json(f)
