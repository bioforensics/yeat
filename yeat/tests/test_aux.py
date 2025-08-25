# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
from yeat.tests import data_file
from yeat.workflow.qc.aux import copy_input


@pytest.mark.parametrize("do_copy, expected_symlink", [(True, False), (False, True)])
def test_copy_input(tmp_path, do_copy, expected_symlink):
    src_file = data_file("short_reads_1.fastq.gz")
    dest_file = tmp_path / "short_reads_1.fastq.gz"
    copy_input(src_file, dest_file, do_copy)
    assert dest_file.exists()
    assert dest_file.is_symlink() == expected_symlink
