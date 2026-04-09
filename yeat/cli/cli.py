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
        help="seed for random number generator used in downsampling (default: random int)",
        metavar="S",
        type=int,
    )
    workflow.add_argument(
        "-t",
        "--threads",
        default=1,
        help="number of threads T for sequential and parallel processing (default: 1)",
        metavar="T",
        type=int,
    )
    workflow.add_argument(
        "-w",
        "--workdir",
        default=".",
        help="working directory (default: current directory)",
        metavar="DIR",
        type=str,
    )
    workflow.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="construct workflow DAG and print summary without execution",
    )
    workflow.add_argument(
        "--copy_input",
        action="store_true",
        help="copy input FASTQ files to the working directory instead of symlinking",
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
    config_template = '''[global_settings.filter]
enabled = true                              # if false, proceed to downsample
min_length = 100                            # adjust for long reads   
quality = 15                                # adjust for long reads  

[global_settings.downsample]
method = "none"                             # if method="none", proceed to assembly; "none"|"random"|"bbnorm"
target_num_reads = 0                        # adjust when downsample="random"; if target_num_reads=0, auto calculate input value using genome_size and target_depth
genome_size = 0                             # adjust when downsample="random" and target_num_reads=0; if genome_size=0, auto calculate input value using MASH
target_depth = 150                          # adjust when downsample="random" and target_num_reads=0

[samples.sample1]
illumina = "data/short_reads_?.fastq.gz"    # glob path

[assemblers.spades_default]
algorithm = "spades"'''

    def __call__(self, parser, namespace, values, option_string=None):
        print(self.config_template)
        raise SystemExit()
