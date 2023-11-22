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
from yeat.config import ILLUMINA_READS, LONG_READS


FINAL_FILES = {
    "spades": "contigs.fasta",
    "megahit": "final.contigs.fa",
    "unicycler": "assembly.fasta",
    "flye": "assembly.fasta",
    "canu": "*.contigs.fasta",
    "hifiasm": "*.bp.p_ctg.fa",
    "hifiasm_meta": "*.p_ctg.fa",
    "metamdbg": "contigs.fasta.gz",
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
    return config, data


def run_yeat(arglist):
    args = cli.get_parser().parse_args(arglist)
    main(args)


def get_expected(algorithm, wd, data):
    analysis_dir = Path(wd).resolve() / "analysis"
    expected = []
    for assembly_label, assembly_obj in data["assemblies"].items():
        for sample_label in assembly_obj["samples"]:
            sample_obj = data["samples"][sample_label]
            short_readtype = set(sample_obj).intersection(ILLUMINA_READS)
            long_readtype = set(sample_obj).intersection(LONG_READS)
            if assembly_obj["mode"] in ["paired", "single"]:
                expected.append(
                    analysis_dir
                    / sample_label
                    / next(iter(short_readtype))
                    / assembly_label
                    / assembly_obj["algorithm"]
                    / FINAL_FILES[algorithm].replace("*", sample_label)
                )
            elif assembly_obj["mode"] in ["pacbio", "oxford"]:
                expected.append(
                    analysis_dir
                    / sample_label
                    / next(iter(long_readtype))
                    / assembly_label
                    / assembly_obj["algorithm"]
                    / FINAL_FILES[algorithm].replace("*", sample_label)
                )
    return expected


def files_exist(expected):
    for x in expected:
        assert x.exists()
