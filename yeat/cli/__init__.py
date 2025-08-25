# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .cli import get_parser
from yeat.workflow import run_workflow


def main(args=None):
    if args is None:
        args = get_parser().parse_args()  # pragma: no cover
    run_workflow(
        config=args.config,
        seed=args.seed,
        threads=args.threads,
        workdir=args.workdir,
        dry_run=args.dry_run,
        copy_input=args.copy_input,
    )
