# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import cli
from .config import AssemblerConfig
from yeat.bandage import bandage
from yeat.workflows import workflows


def main(args=None):
    if args is None:
        args = cli.get_parser().parse_args()
    assembly_configs = AssemblerConfig.parse_json(open(args.config))
    workflows.run_workflow(args, assembly_configs)
    # if not args.dry_run:
    #     bandage.run_bandage(
    #         assembly_configs=assembly_configs, outdir=args.outdir, cores=args.threads
    #     )
