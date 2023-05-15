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


def test_pacbio_hifi_assemblers_dry_run(tmp_path):
    wd = str(tmp_path)
    arglist = [
        "--outdir",
        wd,
        "-n",
        "-t",
        "4",
        data_file("configs/pacbio.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)


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


@pytest.mark.hifi
@pytest.mark.parametrize(
    "algorithm,label,expected",
    [
        ("canu", "canu-default", "sample.contigs.fasta"),
        ("flye", "flye-default", "assembly.fasta"),
    ],
)
def test_pacbio_hifi_read_assemblers(algorithm, label, expected, capsys, tmp_path):
    wd = str(tmp_path)
    cores = str(multiprocessing.cpu_count())
    arglist = [
        "--outdir",
        wd,
        "--threads",
        cores,
        data_file(f"configs/{algorithm}.cfg"),
    ]
    args = cli.get_parser().parse_args(arglist)
    cli.main(args)
    observed = Path(wd).resolve() / "analysis" / "sample1" / label / algorithm / expected
    assert observed.exists()
