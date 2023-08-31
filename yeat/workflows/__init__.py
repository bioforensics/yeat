# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import bandage
from importlib.resources import files
from snakemake import snakemake


def run_paired(args, config):
    snakefile = files("yeat") / "workflows" / "snakefiles" / "Paired"
    data = config.to_dict(args, readtype="paired")
    success = snakemake(
        snakefile,
        config=data,
        cores=args.threads,
        dryrun=args.dry_run,
        printshellcmds=True,
        workdir=args.outdir,
    )
    if not success:
        raise RuntimeError("Snakemake Failed")  # pragma: no cover


def run_single(args, config):
    snakefile = files("yeat") / "workflows" / "snakefiles" / "Single"
    data = config.to_dict(args, readtype="single")
    success = snakemake(
        snakefile,
        config=data,
        cores=args.threads,
        dryrun=args.dry_run,
        printshellcmds=True,
        workdir=args.outdir,
    )
    if not success:
        raise RuntimeError("Snakemake Failed")  # pragma: no cover


def run_pacbio(args, config):
    snakefile = files("yeat") / "workflows" / "snakefiles" / "Pacbio"
    data = config.to_dict(args, readtype="pacbio")
    success = snakemake(
        snakefile,
        config=data,
        cores=args.threads,
        dryrun=args.dry_run,
        printshellcmds=True,
        workdir=args.outdir,
    )
    if not success:
        raise RuntimeError("Snakemake Failed")  # pragma: no cover


def run_oxford(args, config):
    snakefile = files("yeat") / "workflows" / "snakefiles" / "Oxford"
    data = config.to_dict(args, readtype="oxford")
    success = snakemake(
        snakefile,
        config=data,
        cores=args.threads,
        dryrun=args.dry_run,
        printshellcmds=True,
        workdir=args.outdir,
    )
    if not success:
        raise RuntimeError("Snakemake Failed")  # pragma: no cover


def run_workflows(args, config):
    if config.batch["paired"]["assemblers"]:
        run_paired(args, config)
    if config.batch["single"]["assemblers"]:
        run_single(args, config)
    if config.batch["pacbio"]["assemblers"]:
        run_pacbio(args, config)
    if config.batch["oxford"]["assemblers"]:
        run_oxford(args, config)
    if not args.dry_run:
        bandage.run_bandage(args, config)
