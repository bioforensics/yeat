# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import gzip
from pathlib import Path
from shutil import copy, copyfileobj


def copy_input(src, dst, do_copy):
    if not is_gzip(src):
        compress(src, dst)
        return
    if do_copy:
        copy(src, dst)
    else:
        Path(dst).symlink_to(src)


def is_gzip(path):
    with open(path, "rb") as f:
        return f.read(2) == b"\x1f\x8b"


def compress(src, dst):
    with open(src, "rb") as f_in, gzip.open(dst, "wb") as f_out:
        copyfileobj(f_in, f_out)
