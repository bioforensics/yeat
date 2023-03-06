# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import short, long


def run_shortread_workflow(args, assembly_configs):
    if args.paired:
        short.run_paired(
            *args.paired,
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
    # elif args.single:
    # elif args.interleaved:


def run_longread_workflow(args, assembly_configs):
    if args.pacbio:
        long.run_pacbio(
            args.pacbio,
            assembly_configs=assembly_configs,
            outdir=args.outdir,
            cores=args.threads,
            sample=args.sample,
            dryrun=args.dry_run,
        )
    # elif args.single:
    # elif args.interleaved:


def run_workflow(args, assembly_configs):
    if args.readtype == "short":
        run_shortread_workflow(args, assembly_configs)
    elif args.readtype == "long":
        run_longread_workflow(args, assembly_configs)
