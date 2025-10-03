# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from argparse import ArgumentParser, Action
from importlib.metadata import version
from pathlib import Path
from random import randint
import sys
import toml


def get_parser(exit_on_error=True):
    parser = ArgumentParser(add_help=False, exit_on_error=exit_on_error)
    workflow_inputs(parser)
    options(parser)
    workflow_configuration(parser)
    grid_configuration(parser)
    return parser


def workflow_inputs(parser):
    parser._positionals.title = "Workflow Inputs"
    parser.add_argument(
        "config",
        help="path to configuration file",
        type=lambda config: str(Path(config).resolve()),
    )


def options(parser):
    parser._optionals.title = "Options"
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help="show this help message and exit",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"YEAT v{version('yeat')}",
    )
    parser.add_argument(
        "--init",
        action=InitAction,
        nargs=0,
        help="print a template config file to the terminal (stdout) and exit",
    )


def workflow_configuration(parser):
    workflow = parser.add_argument_group("Workflow Configurations")
    workflow.add_argument(
        "-s",
        "--seed",
        default=randint(1, 2**16 - 1),
        help="seed for the random number generator used for downsampling; by default, the seed is chosen randomly",
        metavar="S",
        type=int,
    )
    workflow.add_argument(
        "-t",
        "--threads",
        default=1,
        help="number of available T threads for sequential and parallel processing jobs; by default, T=1",
        metavar="T",
        type=int,
    )
    workflow.add_argument(
        "-w",
        "--workdir",
        default=".",
        help="working directory; default is current working directory",
        metavar="DIR",
        type=str,
    )
    workflow.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="construct workflow DAG and print a summary but do not execute",
    )
    workflow.add_argument(
        "--copy_input",
        action="store_true",
        help="copy input Fastq files to the working directory to ensure complete data provenance; by default, input Fastq files are symbolically linked to the working directory",
    )


def grid_configuration(parser):
    grid = parser.add_argument_group("Grid Configurations:")
    grid.add_argument(
        "--slurm",
        action="store_true",
        help="distribute workflow execution on the grid using the SLURM scheduler",
    )
    grid.add_argument(
        "-j",
        "--jobs",
        metavar="J",
        type=int,
        default=1024,
        help="maximum number of jobs to submit to the job scheduler at once; `J=1024` by default; ignored if --slurm mode not enabled",
    )


class InitAction(Action):
    config_template = {
        "global_settings": {
            "target_coverage_depth": 150,
            "target_num_reads": -1,
            "genome_size": 0,
            "min_length": 100,
            "quality": 10,
            "skip_filter": True,
        },
        "samples": {"sample1": {"illumina": "short_reads_?.fastq.gz"}},
        "assemblers": {"spades_default": {"algorithm": "spades"}},
    }

    def __call__(self, parser, namespace, values, option_string=None):
        toml.dump(self.config_template, sys.stdout)
        raise SystemExit()
