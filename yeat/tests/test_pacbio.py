# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
from yeat.tests import data_file, get_core_count, write_config, run_yeat, target_files_exist


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
    cores = get_core_count()
    config = write_config(algorithm, wd, "hifi.cfg")
    arglist = ["-o", wd, "-t", str(cores), config]
    run_yeat(arglist)
    target_files_exist(wd, config, cores)
