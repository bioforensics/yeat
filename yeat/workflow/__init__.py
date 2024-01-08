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


def run_workflow(args):
    snakefile = files("yeat") / "workflow" / "Snakefile"
    config = vars(args)
    config["data"] = resolve_paths(config["config"])
    if args.grid:
        success = snakemake(
            snakefile,
            config=config,
            cores=args.threads,
            dryrun=args.dry_run,
            printshellcmds=True,
            workdir=args.outdir,
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
        )
    if not success:
        raise RuntimeError("Snakemake Failed")  # pragma: no cover


def resolve_paths(infile):
    data = json.load(open(infile))
    for label, sample in data["samples"].items():
        resolved_paths = []
        for readtype, reads in sample.items():
            for read in reads:
                if isinstance(read, list):
                    resolved_paths.append([str(Path(direction).resolve()) for direction in read])
                else:
                    resolved_paths.append(str(Path(read).resolve()))
        sample[readtype] = resolved_paths
    return data


def setup_grid_args(args):
    if args.grid_args is not None:
        return args.grid_args
    grid_args = " -V "
    if args.threads > 1:
        grid_args = f" -V -pe threads {args.threads} "
    return grid_args
