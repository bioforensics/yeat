# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
from yeat.tests import *


@pytest.mark.short
def test_pacbio_hifi_assemblers_dry_run(tmp_path):
    wd = str(tmp_path)
    arglist = ["-o", wd, "-n", "-t", "4", data_file("configs/hifi.cfg")]
    run_yeat(arglist)


@pytest.mark.long
@pytest.mark.hifi
@pytest.mark.parametrize("algorithm", ["flye", "canu", "hifiasm", "unicycler"])
def test_pacbio_hifi_read_assemblers(algorithm, capsys, tmp_path):
    wd = str(tmp_path)
    cores = str(get_core_count())
    config = write_config(algorithm, wd, "hifi.cfg")
    arglist = ["-o", wd, "-t", cores, config]
    run_yeat(arglist)
    expected_files_exist(wd, config, cores)


@pytest.mark.long
@pytest.mark.hifi
@pytest.mark.parametrize("algorithm", ["flye", "hifiasm_meta"])
def test_pacbio_hifi_read_metagenomic_assemblers(algorithm, capsys, tmp_path):
    wd = str(tmp_path)
    cores = str(get_core_count())
    config = write_config(algorithm, wd, "meta.cfg")
    arglist = ["-o", wd, "-t", cores, config]
    run_yeat(arglist)
    expected_files_exist(wd, config, cores)


@pytest.mark.linux
def test_metaMDBG_assembler(tmp_path):
    algorithm = "metamdbg"
    wd = str(tmp_path)
    cores = str(get_core_count())
    config = write_config(algorithm, wd, "meta.cfg")
    arglist = ["-o", wd, "-t", cores, config]
    run_yeat(arglist)
    expected_files_exist(wd, config, cores)
