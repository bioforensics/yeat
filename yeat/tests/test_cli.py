# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from argparse import ArgumentTypeError
import json
import pytest
from yeat.cli import cli
from yeat.cli.cli import InitAction, illumina

pytestmark = pytest.mark.short


def test_display_config_template(capsys):
    with pytest.raises(SystemExit):
        InitAction.__call__(None, None, None, None)
    out, err = capsys.readouterr()
    assert json.loads(out) == cli.CONFIG_TEMPLATE


@pytest.mark.parametrize("value", [1, 10, 100])
def test_check_positive_valid_values(value):
    illumina.check_positive(value) == value


@pytest.mark.parametrize("value", [-1, 0])
def test_check_positive_bad_values(value):
    message = f"{value} is not a positive integer"
    with pytest.raises(ArgumentTypeError, match=message):
        illumina.check_positive(value)


# rename function here
def test_check_positive_bad_values2():
    message = f"BAD is not an integer"
    with pytest.raises(ArgumentTypeError, match=message):
        illumina.check_positive("BAD")
