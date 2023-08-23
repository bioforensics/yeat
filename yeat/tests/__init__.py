# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import json
import multiprocessing
import os
from pathlib import Path
from pkg_resources import resource_filename


def data_file(path):
    pathparts = path.split("/")
    relpath = os.path.join("tests", "data", *pathparts)
    return resource_filename("yeat", relpath)


def get_core_count():
    return multiprocessing.cpu_count()


def write_config(labels, wd, cfg):
    data = json.load(open(data_file(f"configs/{cfg}")))
    assemblers = []
    for assembler in data["assemblers"]:
        if assembler["label"] in labels:
            assemblers.append(assembler)
    data["assemblers"] = assemblers
    json.dump(data, open(Path(wd) / cfg, "w"))
    return assemblers


def files_exists(wd, assemblers, expected):
    analysis_dir = Path(wd).resolve() / "analysis"
    for assembler in assemblers:
        for sample in assembler["samples"]:
            label = assembler["label"]
            algorithm = assembler["algorithm"]
            assert (analysis_dir / sample / label / algorithm / expected).exists()
