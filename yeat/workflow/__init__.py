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
from snakemake import snakemake
import subprocess
import warnings
from .aux import get_slurm_logs_dir
from yeat.config import READ_TYPES


import toml


def run_workflow(args):
    snakefile = files("yeat") / "workflow" / "Snakefile.smk"
    config = vars(args)
    config["config"] = get_config_data(config["config"])
    snakemake_local(args, snakefile, config)

    # print(config)
    # snakemake_local(args, snakefile, config)
    # config["data"] = get_config_data(config["config"])
    # config["bandage"] = check_bandage()
    # if args.grid == "slurm":
    #     success = snakemake_grid_slurm(args, snakefile, config)
    # elif args.grid == True:
    #     success = snakemake_grid_default(args, snakefile, config)
    # else:
    #     success = snakemake_local(args, snakefile, config)
    # if not success:
    #     raise RuntimeError("Snakemake Failed")  # pragma: no cover


def get_config_data(infile):
    # data = toml.load(open(infile))
    # print(data)
    # assert 0
    # for sample in data["samples"].values():
    #     resolve_sample_paths(sample)
    # return data

    data = toml.load(open(infile))

    for sample_label, sample_data in data["samples"].items():
        for readtype, reads in sample_data.items():
            if isinstance(reads, list):
                data["samples"][sample_label][readtype] = [
                    str(Path(direction).resolve()) for direction in reads
                ]
            else:
                data["samples"][sample_label][readtype] = str(Path(reads).resolve())
    return data


def resolve_sample_paths(sample):
    readtypes = set(sample.keys()).intersection(set(READ_TYPES))
    for readtype in readtypes:
        sample[readtype] = get_resolved_paths(sample[readtype])


def get_resolved_paths(reads):
    resolved_paths = []
    for read in reads:
        if isinstance(read, list):
            resolved_paths.append([str(Path(direction).resolve()) for direction in read])
        else:
            resolved_paths.append(str(Path(read).resolve()))
    return resolved_paths


def check_bandage():
    try:
        completed_process = subprocess.run(["Bandage", "--help"], capture_output=True, text=True)
    except Exception as exception:
        print(f"{type(exception).__name__}: {exception}")
        warnings.warn("Unable to run Bandage; skipping Bandage")
        return False
    if completed_process.returncode == 1:
        print(completed_process.stderr)
        warnings.warn("Unable to run Bandage; skipping Bandage")
        return False
    return True


def setup_grid_args(args):
    if args.grid_args is not None:
        return args.grid_args
    if args.grid == "slurm":
        slurm_logs_dir = get_slurm_logs_dir(args.outdir)
        if not Path(slurm_logs_dir).is_dir():
            Path(slurm_logs_dir).mkdir(parents=True, exist_ok=True)
        log_path = f"{slurm_logs_dir}/{{rule}}-{{wildcards.sample}}-%j.log"
        grid_args = f"sbatch -o {log_path} -e {log_path} "
    else:
        grid_args = " -V "
    thread_arg = f"-c {args.threads} " if args.grid == "slurm" else f"-pe threads {args.threads} "
    return grid_args + thread_arg


def snakemake_grid_slurm(args, snakefile, config):
    success = snakemake(
        snakefile,
        config=config,
        dryrun=args.dry_run,
        printshellcmds=True,
        workdir=args.workdir,
        use_conda=True,
        local_cores=args.threads,
        nodes=args.grid_limit,
        cluster=setup_grid_args(args),
        drmaa_log_dir=str((Path(args.workdir) / "gridlogs").resolve()),
    )
    return success


def snakemake_grid_default(args, snakefile, config):
    success = snakemake(
        snakefile,
        config=config,
        dryrun=args.dry_run,
        printshellcmds=True,
        workdir=args.workdir,
        use_conda=True,
        local_cores=args.threads,
        nodes=args.grid_limit,
        drmaa=setup_grid_args(args),
        drmaa_log_dir=str((Path(args.workdir) / "gridlogs").resolve()),
    )
    return success


def snakemake_local(args, snakefile, config):
    success = snakemake(
        snakefile,
        config=config,
        cores=args.threads,
        dryrun=args.dry_run,
        printshellcmds=True,
        workdir=args.workdir,
        use_conda=True,
    )
    return success
