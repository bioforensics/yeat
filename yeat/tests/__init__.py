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
from pathlib import Path
from importlib.resources import files
from yeat.cli import main, cli
from yeat.config.config import AssemblyConfig


FINAL_FILES = {
    "spades": "contigs.fasta",
    "megahit": "final.contigs.fa",
    "unicycler": "assembly.fasta",
    "flye": "assembly.fasta",
    "canu": "*.contigs.fasta",
    "hifiasm": "*.bp.p_ctg.gfa",
    "hifiasm_meta": "*.p_ctg.gfa",
    "metamdbg": "contigs.fasta",
}


def data_file(path):
    pkg_path = files("yeat") / "tests" / "data" / path
    return str(pkg_path)


def get_core_count():
    return multiprocessing.cpu_count()


def write_config(algorithm, wd, filename):
    data = json.load(open(data_file(f"configs/{filename}")))
    assemblies = {
        label: assembly
        for label, assembly in data["assemblies"].items()
        if assembly["algorithm"] == algorithm
    }
    data["assemblies"] = assemblies
    config = str(Path(wd) / filename)
    json.dump(data, open(config, "w"))
    return config


def run_yeat(arglist):
    args = cli.get_parser().parse_args(arglist)
    main(args)


def targets_exist(wd, config, threads=1):
    cfg = AssemblyConfig(json.load(open(config)), threads)
    assert all([(Path(wd) / file).exists() for file in cfg.targets])
