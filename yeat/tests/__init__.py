# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from importlib.resources import files
import multiprocessing
from yeat.cli import main, cli


def data_file(path):
    pkg_path = files("yeat") / f"tests/data/{path}"
    return str(pkg_path)


def get_core_count():
    return multiprocessing.cpu_count()


def run_yeat(arglist):
    args = cli.get_parser().parse_args(arglist)
    main(args)
