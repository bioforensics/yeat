# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
import toml
from yeat.cli.cli import InitAction


def test_display_config_template(capsys):
    action = InitAction(option_strings=[], dest="init")
    with pytest.raises(SystemExit):
        action(None, None, None, None)
    out, err = capsys.readouterr()
    data = toml.loads(out)
    assert data == InitAction.config_template
