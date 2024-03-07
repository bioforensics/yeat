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


def run_workflow(args):
    snakefile = files("yeat") / "workflow" / "Snakefile"
    config = vars(args)
    config["data"] = resolve_paths(config["config"])
    config["bandage"] = check_bandage()
    if args.grid:
        success = snakemake(
            snakefile,
            config=config,
            cores=args.threads,
            dryrun=args.dry_run,
            printshellcmds=True,
            workdir=args.outdir,
            use_conda=True,
            local_cores=args.threads,
            nodes=args.grid_limit,
            drmaa=setup_grid_args(args),
            drmaa_log_dir=str((Path(args.outdir) / "gridlogs").resolve()),
        )
    else:
        success = snakemake(
            snakefile,
            config=config,
            cores=args.threads,
            dryrun=args.dry_run,
            printshellcmds=True,
            workdir=args.outdir,
            use_conda=True,
        )
    if not success:
        raise RuntimeError("Snakemake Failed")  # pragma: no cover


def resolve_paths(infile):
    data = json.load(open(infile))
    for label, sample in data["samples"].items():
        for readtype, reads in sample.items():
            resolved_paths = []
            for read in reads:
                if isinstance(read, list):
                    resolved_paths.append([str(Path(direction).resolve()) for direction in read])
                else:
                    resolved_paths.append(str(Path(read).resolve()))
            sample[readtype] = resolved_paths
    return data


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
    grid_args = " -V "
    if args.threads > 1:
        grid_args = f" -V -pe threads {args.threads} "
    return grid_args
