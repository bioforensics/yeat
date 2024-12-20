# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
from yeat.tests import get_core_count, write_config, run_yeat, target_files_exist


@pytest.mark.long
@pytest.mark.hifi
@pytest.mark.parametrize("algorithm", ["flye", "hifiasm_meta"])
def test_pacbio_hifi_read_metagenomic_assemblers(algorithm, capsys, tmp_path):
    wd = str(tmp_path)
    cores = get_core_count()
    config = write_config(algorithm, wd, "meta.cfg")
    arglist = ["-o", wd, "-t", str(cores), config]
    run_yeat(arglist)
    target_files_exist(wd, config, cores)


@pytest.mark.linux
def test_metaMDBG_assembler(tmp_path):
    algorithm = "metamdbg"
    wd = str(tmp_path)
    cores = get_core_count()
    config = write_config(algorithm, wd, "meta.cfg")
    arglist = ["-o", wd, "-t", str(cores), config]
    run_yeat(arglist)
    target_files_exist(wd, config, cores)
