# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import gzip
import os
from pathlib import Path
import pytest
import shutil
import subprocess
from unittest.mock import patch
from yeat.bandage import bandage
from yeat.tests import data_file


@pytest.mark.bandage
def test_check_bandage():
    assert bandage.check_bandage()


@patch.dict(os.environ, {"PATH": "ROUGE"})
def test_env_path_has_no_path_to_bandage(capsys):
    bandage.check_bandage()
    out, err = capsys.readouterr()
    assert "No such file or directory: 'Bandage'" in out


@patch("yeat.bandage.bandage.check_bandage")
def test_no_bandage_warning(function_mock):
    function_mock.return_value = False
    with pytest.warns(UserWarning, match=r"Unable to run Bandage; skipping Bandage"):
        bandage.run_bandage(assembly_configs=[])


@pytest.mark.bandage
@pytest.mark.parametrize("file", ["k29.contigs.fastg.gz", "assembly_graph_with_scaffolds.gfa.gz"])
def test_assembly_graph_to_png(file, tmp_path):
    compressed = Path(data_file(file))
    assembly_graph = tmp_path / compressed.stem
    with gzip.open(compressed, "r") as f_in:
        with open(assembly_graph, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    filename = assembly_graph.stem
    jpg = tmp_path / f"{filename}.jpg"
    command = ["Bandage", "image", assembly_graph, jpg]
    subprocess.run(command, check=True)
    assert jpg.exists()


def test_convert_contig_to_fastg(tmp_path):
    contig = data_file("k29.contigs.fa.gz")
    fastg = tmp_path / "k29.contigs.fastg"
    command = f"megahit_toolkit contig2fastg 29 {contig} > {fastg}"
    subprocess.run(command, shell=True, check=True)
    assert fastg.exists()
