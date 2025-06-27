# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from argparse import ArgumentParser, Action
from pathlib import Path
from yeat import __version__


def get_parser(exit_on_error=True):
    parser = ArgumentParser(add_help=False, exit_on_error=exit_on_error)
    parser._positionals.title = "Workflow inputs"
    parser.add_argument(
        "config", help="path to configuration file", type=lambda p: str(Path(p).resolve())
    )
    options(parser)
    workflow_configuration(parser)
    preprocessing_and_qc_configuration(parser)
    grid_configuration(parser)
    return parser


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
        version=f"YEAT v{__version__}",
    )
    parser.add_argument(
        "--init",
        action=InitAction,
        nargs=0,
        help="print a template config file to the terminal (stdout) and exit",
    )


def workflow_configuration(parser):
    workflow = parser.add_argument_group("Workflow Configuration")
    workflow.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="construct workflow DAG and print a summary but do not execute",
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


def preprocessing_and_qc_configuration(parser, just_yeat_it=False):
    illumina = parser.add_argument_group("Preprocessing and Quality Control Settings")
    illumina.add_argument(
        "-s",
        "--seed",
        default=None,
        help="seed for the random number generator used for downsampling; by default, the seed is chosen randomly",
        metavar="S",
        type=int,
    )
    illumina.add_argument(
        "-l",
        "--min-length",
        default=100,
        help="minimum required read length; by default L=100",
        metavar="L",
        type=int,
    )
    if just_yeat_it:
        illumina.add_argument(
            "-d",
            "--downsample",
            default=0,
            help="randomly sample D reads from the input rather than assembling the full set; set D=0 to perform auto-downsampling to a desired level of coverage (see --coverage-depth); set D=-1 to disable downsampling; by default, D=0",
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
            "--coverage-depth",
            default=150,
            help="target an average depth of coverage Cx when auto-downsampling; by default, C=150",
            metavar="C",
            type=int,
        )


def grid_configuration(parser):
    grid = parser.add_argument_group("Grid Configuration")
    grid.add_argument(
        "--grid",
        const=True,
        type=str.lower,
        nargs="?",
        help="process input in batches using parallel processing on a grid. By default, if `--grid` is "
        "invoked with no following arguments, DRMAA will be used to configure jobs on the grid. However, "
        "if the scheduler being used is SLURM, users must provide `slurm` as a following argument to `--grid`",
    )
    grid.add_argument(
        "-g",
        "--grid-limit",
        dest="gridnodes",
        metavar="N",
        type=int,
        default=1024,
        help="limit on the number of concurrent jobs to submit to the grid scheduler; by default N=1024",
    )
    grid.add_argument(
        "-G",
        "--grid-args",
        metavar="A",
        default=None,
        help='additional arguments passed to the scheduler to configure grid execution; " -V " '
        'is passed by default, or " -V -pe threads <T> " ("sbatch -c <T> " if using SLURM) '
        "if --threads is set; this can be used for example to configure grid queue or priority "
        ', e.g., " -q largemem -p -1000 " ("sbatch -p largemem --priority -1000 "); '
        'note that when overriding the defaults, the user must explicitly add the " -V " ("sbatch") and threads '
        "configuration if those are still desired",
    )


class InitAction(Action):
    config_template = '''[sample.sample1]
illumina: ['path/to/data/sample1_R1.fastq.gz', 'path/to/data/sample1_R2.fastq.gz']

[sample.sample2]
ont: path/to/data/sample3_ont.fastq.gz

[sample.sample3]
pacbio: path/to/data/sample4_hifi.fastq.gz

[assemblies.short_paired]
algorithm = "spades"
mode = "paired"

[assemblies.long_ont]
algorithm = "flye"
mode = "ont"

[assemblies.long_hifi]
algorithm = "flye"
mode = "pacbio"'''

    def __call__(self, parser, namespace, values, option_string=None):
        print(self.config_template)
        raise SystemExit()
