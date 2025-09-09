# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from importlib.resources import files
from pathlib import Path
from random import randint
from snakemake import snakemake
import toml
from yeat.config.sample import READ_TYPES


def run_workflow(
    config, seed=randint(1, 2**16 - 1), threads=1, workdir=".", dry_run=False, copy_input=False
):
    snakefile = files("yeat") / "workflow" / "yeat.smk"
    snakemake_config = {
        "config": get_config_data(config),
        "seed": seed,
        "threads": threads,
        "workdir": workdir,
        "dry_run": dry_run,
        "copy_input": copy_input,
    }
    success = snakemake_local(snakefile, snakemake_config)
    if not success:
        raise RuntimeError("Snakemake Failed")  # pragma: no cover


def get_config_data(infile):
    data = toml.load(open(infile))
    for sample_label, sample_data in data["samples"].items():
        for readtype, reads in sample_data.items():
            if readtype not in READ_TYPES:
                continue
            if isinstance(reads, str):
                reads = Path(reads).resolve()
                reads = list(reads.parent.glob(reads.name))
            data["samples"][sample_label][readtype] = [str(read) for read in reads]
    return data


def snakemake_local(snakefile, snakemake_config):
    success = snakemake(
        snakefile,
        config=snakemake_config,
        cores=snakemake_config["threads"],
        dryrun=snakemake_config["dry_run"],
        printshellcmds=True,
        workdir=snakemake_config["workdir"],
        use_conda=True,
    )
    return success
