import argparse
import os
from pkg_resources import resource_filename
from snakemake import snakemake
import yeat


def add_args(parser):
    parser.add_argument(
        "-r1", type=str, nargs=1, metavar="file_name", default=None, help="read 1", required=True
    )
    parser.add_argument(
        "-r2",
        type=str,
        nargs=1,
        metavar="file_name",
        default=None,
        help="read 2",
        required=True,
    )
    parser.add_argument(
        "-o",
        type=str,
        nargs=1,
        metavar="out_directory",
        default=".",
        help="out directory; default is current directory",
    )
    parser.add_argument(
        "-c",
        "--cores",
        type=int,
        nargs=1,
        metavar="cores",
        default=1,
        help="number of cores for snakemake; default is 1",
    )
    parser.add_argument("-v", "--version", action="version", version=f"YEAT v{yeat.__version__}")


def run(read1, read2, output=".", cores=1):
    rel_path = os.path.join("Snakefile")
    snakefile = resource_filename("yeat", rel_path)
    config = dict(read1=read1, read2=read2, output=output, cores=cores)
    success = snakemake(
        snakefile,
        config=config,
        cores=cores,
        dryrun="dry",
        printshellcmds=True,
    )
    if not success:
        raise RuntimeError("Snakemake Failed")


def main():
    parser = argparse.ArgumentParser()
    add_args(parser)
    args = parser.parse_args()
    run(args.r1, args.r2, output=args.o, cores=args.cores)
