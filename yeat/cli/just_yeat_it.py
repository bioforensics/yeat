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
        help="reads in FASTQ format; provide 2 for paired; provide 1 for single",
        nargs="+",
        type=lambda p: str(Path(p).resolve()),
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
    filter.add_argument(
        "--filter",
        action="store_true",
        help="enable read filtering (default: disabled)",
    )
    filter.add_argument(
        "--fastp-args",
        default="--min-length 50 --detect_adapter_for_pe",
        help='additional fastp arguments (default: "--min-length 50 --detect_adapter_for_pe")',
        metavar="STR",
        type=str,
    )


def downsample_configuration(parser):
    downsample = parser.add_argument_group("downsample configuration")
    downsample.add_argument(
        "--downsample",
        action="store_true",
        help="enable downsampling (default: disabled)",
    )
    downsample.add_argument(
        "--method",
        choices=["random", "bbnorm"],
        default="random",
        help='downsampling method: "random" for random subsampling or "bbnorm" for digital normalization; other downsampling parameters are ignored when using "bbnorm" (default: "random")',
    )
    downsample.add_argument(
        "-c",
        "--target-depth",
        default=150,
        help="target coverage depth for automatic downsampling (default: 150)",
        metavar="C",
        type=int,
    )
    downsample.add_argument(
        "-d",
        "--target-num-reads",
        default="auto",
        help='target number of reads to downsample to (int), or use "auto" to calculate from --target-depth and --genome-size (default: "auto")',
        metavar="D",
    )
    downsample.add_argument(
        "-g",
        "--genome-size",
        default="auto",
        help='known sample genome size (int), or use "auto" to estimate using Mash (default: "auto")',
        metavar="G",
    )


def sample_configuration(parser):
    sample = parser.add_argument_group("sample configuration")
    sample.add_argument(
        "--sample-label",
        default="sample1",
        help='sample label (default: "sample1")',
        metavar="STR",
        type=str,
    )


def algorithm_configuration(parser):
    algorithm = parser.add_argument_group("algorithm configuration")
    algorithm.add_argument(
        "--assembly-label",
        default="assembly1",
        help='assembly label (default: "assembly1")',
        metavar="STR",
        type=str,
    )
    algorithm.add_argument(
        "--algorithm",
        choices=["spades", "megahit", "unicycler"],
        default="spades",
        help='assembly algorithm (default: "spades")',
    )
    algorithm.add_argument(
        "--arguments",
        default="--isolate",
        help='additional assembly algorithm arguments (default: "--isolate")',
        metavar="STR",
        type=str,
    )


def create_config(args):
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    config = workdir / "config.toml"
    with open(config, "w") as f:
        data = get_config_data(args)
        toml.dump(data, f)
    args.config = str(config.resolve())


def get_config_data(args):
    filter = {"short": {"enabled": args.filter, "fastp_args": args.fastp_args}}
    downsample = {
        "short": {
            "enabled": args.downsample,
            "method": args.method,
            "target_depth": args.target_depth,
            "target_num_reads": args.target_num_reads,
            "genome_size": args.genome_size,
        }
    }
    return {
        "samples": {
            args.sample_label: {
                "illumina": args.read,
                "filter": filter,
                "downsample": downsample,
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
