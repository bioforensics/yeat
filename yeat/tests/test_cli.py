import os
import pytest
import yeat
from yeat import cli
from yeat.tests import data_file


# the purpose of this test is to check if the snakemake workflow is properly defined.
def test_basic_dry_run(tmp_path):
    wd = str(tmp_path)
    os.makedirs(wd, exist_ok=True)
    arglist = [
        "-r1",
        data_file("Animal_289_R1.fq.gz"),
        "-r2",
        data_file("Animal_289_R2.fq.gz"),
        "-o",
        wd,
        "--sample",
        "Animal_289",
        "-n",
    ]
    parser = yeat.cli.get_parser()
    yeat.cli.add_args(parser)
    args = parser.parse_args(arglist)
    yeat.cli.main(args)
