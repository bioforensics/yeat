# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from importlib.resources import files
import json
from pathlib import Path
from random import randint
import subprocess
import toml
from yeat.config.sample import READ_TYPES


def run_workflow(
    config,
    seed=randint(1, 2**16 - 1),
    threads=1,
    workdir=".",
    dry_run=False,
    copy_input=False,
    slurm=False,
    max_jobs=1024,
):
    snakefile = files("yeat") / "workflow" / "Yeat.smk"
    snakemake_config = write_snakemake_config(config, seed, threads, workdir, dry_run, copy_input)
    command = [
        "snakemake",
        "--snakefile",
        snakefile,
        "--directory",
        workdir,
        "--configfile",
        snakemake_config,
        "--printshellcmds",
    ]
    if slurm:
        command.extend(("--executor", "slurm", "--jobs", max_jobs))
    else:
        command.extend(("--cores", threads))
    if dry_run:
        command.append("--dryrun")
    command = list(map(str, command))
    process = subprocess.run(command)
    if process.returncode != 0:
        raise RuntimeError("Snakemake Failed")


def write_snakemake_config(config, seed, threads, workdir, dry_run, copy_input):
    snakemake_config = {
        "config": get_config_data(config),
        "seed": seed,
        "threads": threads,
        "workdir": workdir,
        "dry_run": dry_run,
        "copy_input": copy_input,
    }
    Path(workdir).mkdir(parents=True, exist_ok=True)
    config_file = f"{workdir}/snakemake.cfg"
    with open(config_file, "w") as f:
        json.dump(snakemake_config, f, indent=4)
    return config_file


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
