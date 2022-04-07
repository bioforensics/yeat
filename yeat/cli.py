# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import argparse
from pathlib import Path
from pkg_resources import resource_filename
from snakemake import snakemake
import yeat


ASSEMBLY_ALGORITHMS = ["spades", "megahit"]


def check_assemblies(assembly):
    algorithms = []
    for algorithm in assembly:
        if algorithm not in ASSEMBLY_ALGORITHMS:
            message = (
                f"Found unsupported assembly algorithm with `--assembly` flag: [[{algorithm}]]!"
            )
            raise ValueError(message)
        if algorithm in algorithms:
            message = (
                f"Found duplicate assembly algorithm with `--assembly` flag: [[{algorithm}]]!"
            )
            raise ValueError(message)
        algorithms.append(algorithm)
    return algorithms


def run(read1, read2, assembly, outdir=".", cores=1, sample="sample", dryrun="dry"):
    snakefile = resource_filename("yeat", "Snakefile")
    r1 = Path(read1).resolve()
    r2 = Path(read2).resolve()
    config = dict(
        read1=r1,
        read2=r2,
        assembly=assembly,
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


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=f"YEAT v{yeat.__version__}")
    parser.add_argument(
        "-o",
        "--outdir",
        type=str,
        metavar="DIR",
        default=".",
        help="output directory; default is '.'",
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        metavar="T",
        default=1,
        help="number of threads for Snakemake; default is 1",
    )
    parser.add_argument(
        "--sample",
        type=str,
        metavar="S",
        default="sample",
        help="sample name for Snakemake; default is 'sample'",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="construct workflow DAG and print a summary but do not execute",
    )
    required = parser.add_argument_group("required arguments")
    required.add_argument(
        "--assembly",
        required=True,
        type=str,
        help="assembly algorithm(s); For example, `spades`, `megahit`, or `spades,megahit`",
    )
    parser.add_argument("reads", type=str, nargs=2, help="paired-end reads in FASTQ format")
    return parser


def main(args=None):
    if args is None:
        args = get_parser().parse_args()
    assert len(args.reads) == 2
    assembly = list(filter(None, args.assembly.strip().split(",")))
    assembly = check_assemblies(assembly)
    run(
        *args.reads,
        assembly=assembly,
        outdir=args.outdir,
        cores=args.threads,
        sample=args.sample,
        dryrun=args.dry_run,
    )
