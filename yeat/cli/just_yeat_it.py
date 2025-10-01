# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from argparse import ArgumentParser, ArgumentTypeError
from importlib.metadata import version
from pathlib import Path
import toml
from yeat.workflow import run_workflow
from yeat.cli.cli import workflow_configuration


def main(args=None):
    if args is None:
        args = get_parser().parse_args()  # pragma: no cover
    create_config(args)
    add_config(args)
    run_workflow(
        config=args.config,
        seed=args.seed,
        threads=args.threads,
        workdir=args.workdir,
        dry_run=args.dry_run,
        copy_input=args.copy_input,
    )


def get_parser(exit_on_error=True):
    parser = ArgumentParser(exit_on_error=exit_on_error)
    positional_args(parser)
    options(parser)
    workflow_configuration(parser)
    filter_configuration(parser)
    downsample_configuration(parser)
    sample_configuration(parser)
    algorithm_configuration(parser)
    return parser


def positional_args(parser):
    parser._positionals.title = "required arguments"
    parser.add_argument(
        "read",
        nargs="+",
        type=absolute_path,
        help="reads in FASTQ format; provide 2 for paired; provide 1 for single",
    )


def absolute_path(path_str):
    return str(Path(path_str).resolve())


def options(parser):
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"YEAT v{version('yeat')}",
    )


def filter_configuration(parser):
    illumina = parser.add_argument_group("filter configuration")
    filter_group = illumina.add_mutually_exclusive_group()
    filter_group.add_argument(
        "--skip-filter",
        dest="skip_filter",
        action="store_true",
        help="Skip the filtering step (default)",
    )
    filter_group.add_argument(
        "--no-skip-filter",
        dest="skip_filter",
        action="store_false",
        help="Do not skip the filtering step",
    )
    illumina.add_argument(
        "-l",
        "--length-required",
        default=100,
        help="discard reads shorter than the required L length after pre-preocessing; by default, L=100",
        metavar="L",
        type=int,
    )


def downsample_configuration(parser):
    illumina = parser.add_argument_group("downsample configuration")
    illumina.add_argument(
        "-d",
        "--target-num-reads",
        default=-1,
        help="randomly sample D reads from the input rather than assembling the full set; set D=0 to perform auto-downsampling to a desired level of coverage (see --target-coverage-depth); set D=-1 to disable downsampling; by default, D=-1",
        metavar="D",
        type=int,
    )
    illumina.add_argument(
        "-g",
        "--genome-size",
        default=0,
        help="provide known genome size in base pairs (bp); by default, G=0",
        metavar="G",
        type=int,
    )
    illumina.add_argument(
        "-c",
        "--target-coverage-depth",
        default=150,
        help="target an average depth of coverage Cx when auto-downsampling; by default, C=150",
        metavar="C",
        type=check_positive,
    )


def check_positive(value):
    try:
        value = int(value)
        if value <= 0:
            raise ArgumentTypeError(f"{value} is not a positive integer")
    except ValueError:
        raise ArgumentTypeError(f"{value} is not an integer")
    return value


def sample_configuration(parser):
    sample = parser.add_argument_group("sample configuration")
    sample.add_argument(
        "--sample-label",
        default="sample1",
        help='set the sample label; by default, "sample1"',
        metavar="STR",
    )


def algorithm_configuration(parser):
    algorithm = parser.add_argument_group("algorithm configuration")
    algorithm.add_argument(
        "--assembly-label",
        default="assembly1",
        help='set the assembly label; by default, "assembly1"',
        metavar="STR",
    )
    algorithm.add_argument(
        "--algorithm",
        default="spades",
        help='substitute the default assembly algorithm with another algorithm; for example, "megahit" or "unicycler"; by default, "spades"',
        metavar="STR",
    )
    algorithm.add_argument(
        "--arguments",
        default="",
        help='add assembly algorithm flags; for example, "--meta" or "--isolate --careful" for SPAdes; by default, empty string',
        metavar="STR",
    )


def create_config(args):
    data = get_config_data(args)
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    outfile = open(workdir / "config.toml", "w")
    toml.dump(data, outfile)


def get_config_data(args):
    return {
        "samples": {
            args.sample_label: {
                "illumina": args.read,
                "skip_filter": args.skip_filter,
                "min_length": args.length_required,
                "target_num_reads": args.target_num_reads,
                "genome_size": args.genome_size,
                "target_coverage_depth": args.target_coverage_depth,
            },
        },
        "assemblers": {
            args.assembly_label: {
                "algorithm": args.algorithm,
                "arguments": args.arguments,
                "samples": [args.sample_label],
            }
        },
    }


def add_config(args):
    config = Path(args.workdir) / "config.toml"
    setattr(args, "config", str(config.resolve()))
