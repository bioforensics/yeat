import argparse
import os
from pkg_resources import resource_filename
from snakemake import snakemake
import yeat


def add_args(parser):
    parser.add_argument("-v", "--version", action="version", version=f"YEAT v{yeat.__version__}")
    parser.add_argument(
        "-O",
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
    parser.add_argument("reads", type=str, nargs=2, help="paired-end reads in FASTQ format")


def run(read1, read2, outdir=".", cores=1, sample="sample", dryrun="dry"):
    rel_path = os.path.join("Snakefile")
    snakefile = resource_filename("yeat", rel_path)
    config = dict(
        read1=os.path.abspath(read1),
        read2=os.path.abspath(read2),
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
    return parser


def main(args=None):
    if args is None:
        parser = get_parser()
        add_args(parser)
        args = parser.parse_args()
    read1, read2 = args.reads
    run(
        read1,
        read2,
        outdir=args.outdir,
        cores=args.threads,
        sample=args.sample,
        dryrun=args.dry_run,
    )
