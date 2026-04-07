# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from argparse import ArgumentParser
from importlib.metadata import version
from pathlib import Path
import toml
from yeat.workflow import run_workflow
from yeat.cli.cli import workflow_configuration


def main(args=None):
    if args is None:
        args = get_parser().parse_args()  # pragma: no cover
    create_config(args)
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
        type=lambda p: str(Path(p).resolve()),
        help="reads in FASTQ format; provide 2 for paired; provide 1 for single",
    )


def options(parser):
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"YEAT v{version('yeat')}",
    )


def filter_configuration(parser):
    filter = parser.add_argument_group("filter configuration")
    group = filter.add_mutually_exclusive_group()
    group.add_argument(
        "--filter",
        dest="filter",
        action="store_true",
        help="enable read filtering (default: enabled)",
    )
    group.add_argument(
        "--no-filter",
        dest="filter",
        action="store_false",
        help="disable read filtering (ignores -l, -q)",
    )
    parser.set_defaults(filter_enabled=True)
    filter.add_argument(
        "-l",
        "--length-required",
        default=100,
        help="discard reads shorter than length L (default: 100)",
        metavar="L",
        type=int,
    )
    filter.add_argument(
        "-q",
        "--quality",
        default=15,
        help="minimum base quality threshold Q for filtering (default: 15)",
        metavar="Q",
        type=int,
    )


def downsample_configuration(parser):
    downsample = parser.add_argument_group("downsample configuration")
    downsample.add_argument(
        "--downsample-method",
        choices=["none", "random", "bbnorm"],
        default="none",
        help='Downsampling method: "none" (disable), "random" (subsample reads), "bbnorm" (digital normalization; ignores other downsampling params)',
    )
    downsample.add_argument(
        "-d",
        "--target-num-reads",
        default=0,
        help='number of reads D to sample in "random" mode (ignores -g, -c); D=0 enables automatic downsampling using -g and -c (default: 0)',
        metavar="D",
        type=int,
    )
    downsample.add_argument(
        "-g",
        "--genome-size",
        default=0,
        help="estimated genome size G in bp; G=0 enables automatic genome size estimation (default: 0)",
        metavar="G",
        type=int,
    )
    downsample.add_argument(
        "-c",
        "--target-depth",
        default=150,
        help="target coverage depth C for automatic downsampling (default: 150)",
        metavar="C",
        type=int,
    )


def sample_configuration(parser):
    sample = parser.add_argument_group("sample configuration")
    sample.add_argument(
        "--sample-label",
        default="sample1",
        help='sample label (default: "sample1")',
        metavar="STR",
    )


def algorithm_configuration(parser):
    algorithm = parser.add_argument_group("algorithm configuration")
    algorithm.add_argument(
        "--assembly-label",
        default="assembly1",
        help='assembly label (default: "assembly1")',
        metavar="STR",
    )
    algorithm.add_argument(
        "--algorithm",
        default="spades",
        help='assembly algorithm to use (e.g., "megahit", "unicycler"; default: "spades")',
        metavar="STR",
    )
    algorithm.add_argument(
        "--arguments",
        default="",
        help='additional assembler arguments (e.g., "--meta", "--isolate --careful"; default: "")',
        metavar="STR",
    )


def create_config(args):
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    config = workdir / "config.toml"
    with open(config, "w") as f:
        data = get_config_data(args)
        toml.dump(data, f)
    setattr(args, "config", str(config.resolve()))


def get_config_data(args):
    return {
        "samples": {
            args.sample_label: {
                "illumina": args.read,
                "filter": {
                    "enabled": args.filter_enabled,
                    "min_length": args.length_required,
                    "quality": args.quality,
                },
                "downsample": {
                    "method": args.downsample_method,
                    "target_num_reads": args.target_num_reads,
                    "genome_size": args.genome_size,
                    "target_depth": args.target_depth,
                },
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
