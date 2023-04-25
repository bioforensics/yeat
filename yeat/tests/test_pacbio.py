# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import multiprocessing
from pathlib import Path
import pytest
from yeat import cli, workflows
from yeat.tests import data_file


def test_pacbio_hifi_read_assemblers_dry_run(tmp_path):
    wd = str(tmp_path)
    arglist = [
        "--outdir",
        wd,
        "-n",
        "-t",
        "4",
        "--pacbio",
        data_file("ecoli.fastq.gz"),
        data_file("pacbio.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)


def test_invalid_read_file():
    with pytest.raises(Exception, match=r"No such file:.*read\'"):
        read = "read"
        assemblers = ["flye"]
        workflows.run_pacbio(read, assemblers)


@pytest.mark.parametrize(
    "extra_args,cores,expected",
    [
        ("", 4, r"Missing required input argument from config: 'genomeSize'"),
        (
            "genomeSize=4.8m",
            1,
            r"Canu requires at least 4 avaliable cores; increase `--threads` to 4 or more",
        ),
    ],
)
def test_check_canu_required_params_errors(extra_args, cores, expected):
    with pytest.raises(ValueError, match=expected):
        workflows.check_canu_required_params(extra_args, cores)


@pytest.mark.long
@pytest.mark.parametrize(
    "algorithm,finalcontigs",
    [
        ("canu", "sample.contigs.fasta"),
        ("flye", "assembly.fasta"),
    ],
)
def test_pacbio_hifi_read_assemblers(algorithm, finalcontigs, capsys, tmp_path):
    wd = str(tmp_path)
    cores = str(multiprocessing.cpu_count())
    arglist = [
        "--outdir",
        wd,
        "--threads",
        cores,
        "--pacbio",
        data_file("ecoli.fastq.gz"),
        data_file(f"{algorithm}.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    result = Path(wd).resolve() / "analysis" / algorithm / finalcontigs
    assert result.exists()
