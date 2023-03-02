# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import short, long


def run_workflow(args, assembly_configs):
    if args.subparser == "short":
        short.paired.run(
            *args.reads,
            assembly_configs=assembly_configs,
            outdir=args.outdir,
            cores=args.threads,
            sample=args.sample,
            dryrun=args.dry_run,
            downsample=args.downsample,
            coverage=args.coverage,
            seed=args.seed,
            genomesize=args.genome_size,
        )
    elif args.subparser == "long":
        long.pacbio.run(
            args.read,
            assembly_configs=assembly_configs,
            outdir=args.outdir,
            cores=args.threads,
            sample=args.sample,
            dryrun=args.dry_run,
        )
