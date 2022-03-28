# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .cli import get_parser
from pathlib import Path
from pkg_resources import resource_filename
from snakemake import snakemake
from yeat.assembly import config


SNAKEFILES = {"spades": resource_filename("yeat", "assembly/Snakefile_Spades")}


def run(read1, read2, assembler, outdir=".", cores=1, sample="sample", dryrun="dry"):
    snakefile = SNAKEFILES[assembler.algorithm]
    r1 = Path(read1).resolve()
    r2 = Path(read2).resolve()
    config = dict(
        read1=r1,
        read2=r2,
        outdir=outdir,
        cores=cores,
        sample=sample,
        dryrun=dryrun,
    )
    success = snakemake(
        snakefile,
        config=config,
        cores=cores,
        dryrun=dryrun,
        printshellcmds=True,
        workdir=outdir,
    )
    if not success:
        raise RuntimeError("Snakemake Failed")


def main(args=None):
    if args is None:
        args = get_parser().parse_args()
    assert len(args.reads) == 2
    with open(args.config, "r") as fh:
        assemblers = config.AssemblyConfiguration.parse_json(fh)
    for assembler in assemblers:
        run(
            *args.reads,
            assembler=assembler,
            outdir=args.outdir,
            cores=args.threads,
            sample=args.sample,
            dryrun=args.dry_run,
        )
