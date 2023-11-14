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
    snakefile = files("yeat") / "workflows" / "snakefiles" / "Workflow"
    config = vars(args)
    config["data"] = resolve_paths(config["config"])
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
        for readtype, reads in sample.items():
            if readtype == "paired":
                sample[readtype] = [[str(Path(read).resolve()) for read in pair] for pair in reads]
            else:
                sample[readtype] = [str(Path(read).resolve()) for read in reads]
    return data
