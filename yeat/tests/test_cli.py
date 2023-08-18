# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from argparse import ArgumentError
import json
import pytest
from yeat import cli
from yeat.cli import InitAction, illumina
from yeat.tests import data_file


def test_display_config_template(capsys):
    with pytest.raises(SystemExit):
        InitAction.__call__(None, None, None, None)
    out, err = capsys.readouterr()
    assert json.loads(out) == cli.CONFIG_TEMPLATE


@pytest.mark.parametrize("coverage", [("-1"), ("0")])
def test_invalid_custom_coverage_negative(coverage):
    arglist = ["-c", coverage, data_file("paired.cfg")]
    with pytest.raises(ArgumentError, match=rf"{coverage} is not a positive integer"):
        args = cli.get_parser(exit_on_error=False).parse_args(arglist)


@pytest.mark.parametrize("coverage", [("string"), ("3.14")])
def test_invalid_custom_coverage_noninteger(coverage):
    arglist = ["-c", coverage, data_file("paired.cfg")]
    with pytest.raises(ArgumentError, match=rf"{coverage} is not an integer"):
        args = cli.get_parser(exit_on_error=False).parse_args(arglist)


@pytest.mark.parametrize("value", [1, 10, 100])
def test_check_positive(value):
    illumina.check_positive(value) == value
