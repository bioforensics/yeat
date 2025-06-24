# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import illumina
from .aux import InitAction, check_positive
from argparse import ArgumentParser
from pathlib import Path
import yeat


def get_parser(exit_on_error=True):
    parser = ArgumentParser(add_help=False, exit_on_error=exit_on_error)
    options(parser)
    workflow_configuration(parser)
    grid_configuration(parser)
    illumina.fastp_configuration(parser)
    illumina.downsample_configuration(parser)
    parser._positionals.title = "required arguments"
    parser.add_argument("config", help="config file", type=lambda p: str(Path(p).resolve()))
    return parser


def options(parser):
    parser._optionals.title = "options"
    parser.add_argument(
        "--init",
        action=InitAction,
        nargs=0,
        help="print a template assembly config file to the terminal (stdout) and exit",
    )
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
        version=f"YEAT v{yeat.__version__}",
    )


def workflow_configuration(parser):
    workflow = parser.add_argument_group("workflow configuration")
    workflow.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="construct workflow DAG and print a summary but do not execute",
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
        "-t",
        "--threads",
        default=1,
        help="number of available T threads for sequential and parallel processing jobs; by default, T=1",
        metavar="T",
        type=int,
    )


def grid_configuration(parser):
    grid = parser.add_argument_group("grid configuration")
    grid.add_argument(
        "--grid",
        const=True,
        type=str.lower,
        nargs="?",
        help="""process input in batches using parallel processing on a grid. By default, if `--grid` is 
        invoked with no following arguments, DRMAA will be used to configure jobs on the grid. However, 
        if the scheduler being used is SLURM, users must provide `slurm` as a following argument to `--grid`""",
    )
    grid.add_argument(
        "--grid-limit",
        default=1024,
        help="limit on the number of concurrent jobs to submit to the grid scheduler; by default, N=1024",
        metavar="N",
        type=check_positive,
    )
    grid.add_argument(
        "--grid-args",
        default=None,
        help="""additional arguments passed to the scheduler to configure grid execution; " -V " 
        is passed by default, or " -V -pe threads <T> " ("sbatch -o ${log_output} -e ${log_output} -c <T> " if using SLURM) 
        if --threads is set; this can be used for example to configure grid queue or priority, 
        e.g., " -q largemem -p -1000 " ("sbatch -p largemem --priority -1000 "); 
        note that when overriding the defaults, the user must explicitly add the " -V " ("sbatch") and threads 
        configuration if those are still desired""",
        metavar="A",
    )
