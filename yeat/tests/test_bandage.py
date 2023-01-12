# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
import subprocess
from unittest.mock import patch
from yeat.bandage import bandage


def test_checking_bandage():
    assert bandage.check_bandage()


@patch("subprocess.run")
def test_unable_to_run_bandage(function_mock, capsys):
    completed_process = subprocess.CompletedProcess(["bandage", "--help"], 1)
    error_message = "FileNotFoundError: [Errno 2] No such file or directory: 'Bandage'"
    completed_process.stderr = error_message
    function_mock.return_value = completed_process
    bandage.check_bandage()
    captured = capsys.readouterr()
    assert error_message in captured.out


@patch("yeat.bandage.bandage.check_bandage")
def test_no_bandage_warning(function_mock):
    function_mock.return_value = False
    with pytest.warns(UserWarning, match=r"Unable to run Bandage; skipping Bandage"):
        bandage.run_bandage(assembly_configs=[])
