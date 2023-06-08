# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import bandage
from pkg_resources import resource_filename
from snakemake import snakemake


def run_paired(args, config):
    snakefile = resource_filename("yeat", "workflows/snakefiles/Paired")
    data = config.to_dict(args, "paired")
    success = snakemake(
        snakefile,
        config=data,
        cores=args.threads,
        dryrun=args.dry_run,
        printshellcmds=True,
        workdir=args.outdir,
    )
    if not success:
        raise RuntimeError("Snakemake Failed")


def run_pacbio(args, config):
    snakefile = resource_filename("yeat", "workflows/snakefiles/Pacbio")
    data = config.to_dict(args, "pacbio")
    success = snakemake(
        snakefile,
        config=data,
        cores=args.threads,
        dryrun=args.dry_run,
        printshellcmds=True,
        workdir=args.outdir,
    )
    if not success:
        raise RuntimeError("Snakemake Failed")


def run_workflows(args, config):
    if config.batch["paired"]["assemblers"]:
        run_paired(args, config)
    if config.batch["pacbio"]["assemblers"]:
        run_pacbio(args, config)
    if not args.dry_run:
        bandage.run_bandage(args, config)
