import argparse
import os
from pkg_resources import resource_filename
from snakemake import snakemake
import yeat


def add_args(parser):
    parser.add_argument(
        "-r1", type=str, metavar="file_name", default=None, help="read 1", required=True
    )
    parser.add_argument(
        "-r2",
        type=str,
        metavar="file_name",
        default=None,
        help="read 2",
        required=True,
    )
    parser.add_argument(
        "-o",
        type=str,
        metavar="out_directory",
        default=".",
        help="out directory; default is '.'",
    )
    parser.add_argument(
        "-c",
        "--cores",
        type=int,
        metavar="cores",
        default=1,
        help="number of cores for snakemake; default is 1",
    )
    parser.add_argument(
        "--sample",
        type=str,
        metavar="sample_name",
        default="sample",
        help="sample name for snakemake; default is 'sample'",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="construct workflow DAG and print a summary but do not execute",
    )
    parser.add_argument("-v", "--version", action="version", version=f"YEAT v{yeat.__version__}")


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
    run(args.r1, args.r2, outdir=args.o, cores=args.cores, sample=args.sample, dryrun=args.dry_run)
