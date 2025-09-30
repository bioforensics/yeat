# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
import sys
from yeat.tests import data_file, run_yeat, get_core_count, final_contig_files_exist


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
    ],
)
def test_short_assemblers(capsys, tmp_path, config):
    wd = str(tmp_path)
    cores = str(get_core_count())
    if sys.platform == "darwin":
        cores = "1"
    arglist = ["-w", wd, "-t", cores, config]
    run_yeat(arglist)
    final_contig_files_exist(wd, config)


@pytest.mark.long
@pytest.mark.parametrize(
    "config",
    [
        data_file("configs/ont.toml"),
        data_file("configs/pacbio.toml"),
    ],
)
def test_long_assemblers(capsys, tmp_path, config):
    wd = str(tmp_path)
    cores = str(get_core_count())
    arglist = ["-w", wd, "-t", cores, config]
    run_yeat(arglist)
    final_contig_files_exist(wd, config)


@pytest.mark.long
def test_hybrid_assemblers(capsys, tmp_path):
    wd = str(tmp_path)
    cores = str(get_core_count())
    config = data_file("configs/hybrid.toml")
    arglist = ["-w", wd, "-t", cores, config]
    run_yeat(arglist)
    final_contig_files_exist(wd, config)


@pytest.mark.long
def test_metagenomics_assemblers(capsys, tmp_path):
    wd = str(tmp_path)
    cores = str(get_core_count())
    config = data_file("configs/metagenomics.toml")
    arglist = ["-w", wd, "-t", cores, config]
    run_yeat(arglist)
    final_contig_files_exist(wd, config)
