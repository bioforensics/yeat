# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .cli import get_parser, run_spades
from yeat.assembly import config


def main(args=None):
    if args is None:
        args = get_parser().parse_args()
    assert len(args.reads) == 2
    with open(args.config, "r") as fh:
        assemblers = config.AssemblyConfiguration.parse_json(fh)
    for assembler in assemblers:
        if assembler.algorithm == "spades":
            run_spades(
                *args.reads,
                outdir=args.outdir,
                cores=args.threads,
                sample=args.sample,
                dryrun=args.dry_run,
            )
