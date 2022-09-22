# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import argparse
from argparse import Action
import json
from pathlib import Path
from pkg_resources import resource_filename
from snakemake import snakemake
import sys
import yeat
from yeat.config import AssemblerConfig


CONFIG_TEMPLATE = [
    dict(
        algorithm="spades",
        extra_args="--meta",
    ),
    dict(
        algorithm="megahit",
        extra_args="--min-count 5 --min-contig-len 300",
    ),
]


class InitAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        json.dump(CONFIG_TEMPLATE, sys.stdout, indent=4)
        print()
        raise SystemExit()


def run(read1, read2, algorithms, outdir=".", cores=1, sample="sample", dryrun="dry"):
    snakefile = resource_filename("yeat", "Snakefile")
    r1 = Path(read1).resolve()
    if not r1.is_file():
        raise FileNotFoundError(f"No such file: '{r1}'")
    r2 = Path(read2).resolve()
    if not r2.is_file():
        raise FileNotFoundError(f"No such file: '{r2}'")
    assemblers = []
    extraargs = {}
    for algorithm in algorithms:
        assembler = algorithm.algorithm
        assemblers.append(assembler)
        extraargs[assembler] = algorithm.extra_args
    config = dict(
        read1=r1,
        read2=r2,
        assemblers=assemblers,
        extraargs=extraargs,
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
    parser.add_argument(
        "--init",
        action=InitAction,
        nargs=0,
        help="print a template assembly config file to the terminal (stdout) and exit",
    )
    parser.add_argument("config", type=str, help="configfile")
    parser.add_argument("reads", type=str, nargs=2, help="paired-end reads in FASTQ format")
    return parser


def main(args=None):
    if args is None:
        args = get_parser().parse_args()
    algorithms = AssemblerConfig.parse_json(open(args.config))
    run(
        *args.reads,
        algorithms=algorithms,
        outdir=args.outdir,
        cores=args.threads,
        sample=args.sample,
        dryrun=args.dry_run,
    )
