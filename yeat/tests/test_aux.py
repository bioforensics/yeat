# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import gzip
from pathlib import Path
import pytest
import shutil
from yeat.tests import data_file
from yeat.workflow.qc.aux import copy_input


@pytest.mark.parametrize("do_copy, expected_symlink", [(True, False), (False, True)])
def test_copy_input(tmp_path, do_copy, expected_symlink):
    src_file = data_file("short_reads_1.fastq.gz")
    dest_file = tmp_path / "short_reads_1.fastq.gz"
    copy_input(src_file, dest_file, do_copy)
    assert dest_file.exists()
    assert dest_file.is_symlink() == expected_symlink


def decompress_to_tmp(src_path, tmp_path):
    dest_path = tmp_path / src_path.with_suffix("").name
    with gzip.open(src_path, "rb") as f_in:
        with open(dest_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    return dest_path


@pytest.mark.parametrize("do_copy, expected_symlink", [(True, False), (False, False)])
def test_copy_input_decompressed_files(tmp_path, do_copy, expected_symlink):
    src_file = Path(data_file("short_reads_1.fastq.gz"))
    decompressed = decompress_to_tmp(src_file, tmp_path)
    dest_file = tmp_path / decompressed.name
    copy_input(decompressed, dest_file, do_copy)
    assert dest_file.exists()
    assert dest_file.is_symlink() == expected_symlink
