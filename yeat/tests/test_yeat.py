# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
from yeat.tests import data_file, run_yeat, get_core_count


@pytest.mark.parametrize(
    "config",
    [
        data_file("configs/paired.toml"),
        data_file("configs/single.toml"),
        data_file("configs/ont.toml"),
        data_file("configs/pacbio.toml"),
        data_file("configs/hybrid.toml"),
        data_file("configs/metagenomics.toml"),
    ],
)
def test_assemblers_dry_run(tmp_path, config):
    wd = str(tmp_path)
    arglist = ["-w", wd, "-n", config]
    run_yeat(arglist)


@pytest.mark.long
@pytest.mark.parametrize(
    "config",
    [
        data_file("configs/paired.toml"),
        data_file("configs/single.toml"),
        data_file("configs/ont.toml"),
        data_file("configs/pacbio.toml"),
        data_file("configs/hybrid.toml"),
        data_file("configs/metagenomics.toml"),
    ],
)
def test_assemblers(capsys, tmp_path, config):
    wd = str(tmp_path)
    cores = str(get_core_count())
    arglist = ["-w", wd, "-t", cores, config]
    run_yeat(arglist)
