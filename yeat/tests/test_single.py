# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
from yeat.tests import data_file, write_config, run_yeat, expected_files_exist


@pytest.mark.short
def test_single_end_assemblers_dry_run(tmp_path):
    wd = str(tmp_path)
    arglist = ["-o", wd, "-n", data_file("configs/single.cfg")]
    run_yeat(arglist)


@pytest.mark.long
@pytest.mark.illumina
@pytest.mark.parametrize("algorithm", ["spades", "megahit", "unicycler"])
def test_single_end_assemblers(algorithm, capsys, tmp_path):
    wd = str(tmp_path)
    config = write_config(algorithm, wd, "single.cfg")
    arglist = ["-o", wd, config]
    run_yeat(arglist)
    expected_files_exist(wd, config)
