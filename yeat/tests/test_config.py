# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import json
import pytest
from yeat.config import AssemblyConfigError
from yeat.config.config import AssemblyConfig
from yeat.tests import data_file

pytestmark = pytest.mark.short


def test_valid_config():
    data = json.load(open(data_file("configs/example.cfg")))
    config = AssemblyConfig(data, 4)
    assert len(config.samples) == 4
    assert len(config.assemblies) == 3


@pytest.mark.parametrize("key,", ["algorithm", "extra_args", "samples", "mode"])
def test_missing_key_in_config_entry(key):
    data = json.load(open(data_file("configs/paired.cfg")))
    del data["assemblies"]["spades-default"][key]
    pattern = rf"Missing assembly configuration setting\(s\) '{key}'"
    with pytest.raises(AssemblyConfigError, match=pattern):
        AssemblyConfig(data)


@pytest.mark.parametrize("layer", ["base", "sample", "assembly"])
def test_check_valid_keys(layer):
    data = json.load(open(data_file("configs/paired.cfg")))
    if layer == "base":
        data["INVALID1"] = ""
        data["INVALID2"] = ""
    elif layer == "sample":
        data["samples"]["Shigella_sonnei_53G"]["INVALID1"] = ""
        data["samples"]["Shigella_sonnei_53G"]["INVALID2"] = ""
    elif layer == "assembly":
        data["assemblies"]["spades-default"]["INVALID1"] = ""
        data["assemblies"]["spades-default"]["INVALID2"] = ""
    pattern = r"Found unsupported configuration key\(s\) 'INVALID1,INVALID2'"
    with pytest.raises(AssemblyConfigError, match=pattern):
        AssemblyConfig(data)


@pytest.mark.parametrize(
    "mode,sample,assembly",
    [
        ("paired", "sample4", "spades-default"),
        ("pacbio", "sample1", "hicanu"),
        ("oxford", "sample1", "flye_ONT"),
    ],
)
def test_check_sample_readtypes_match_assembly_mode(mode, sample, assembly):
    data = json.load(open(data_file("configs/example.cfg")))
    if mode == "paired":
        data["assemblies"]["spades-default"]["samples"] = [sample]
    elif mode == "pacbio":
        data["assemblies"]["hicanu"]["samples"] = [sample]
    elif mode == "oxford":
        data["assemblies"]["flye_ONT"]["samples"] = [sample]
    pattern = rf"No readtypes in '{sample}' match '{assembly}' assembly mode '{mode}'"
    with pytest.raises(AssemblyConfigError, match=pattern):
        AssemblyConfig(data, 4)


def test_get_target_files():
    data = json.load(open(data_file("configs/example.cfg")))
    cfg = AssemblyConfig(data, 4)
    observed = cfg.target_files
    expected = [
        "seq/fastqc/sample1/paired/r1_combined-reads_fastqc.html",
        "seq/fastqc/sample1/paired/r2_combined-reads_fastqc.html",
        "seq/fastqc/sample2/paired/r1_combined-reads_fastqc.html",
        "seq/fastqc/sample2/paired/r2_combined-reads_fastqc.html",
        "seq/fastqc/sample3/pacbio-hifi/combined-reads_fastqc.html",
        "seq/nanoplot/sample4/nano-hq/raw_LengthvsQualityScatterPlot_dot.pdf",
        "seq/nanoplot/sample4/nano-hq/filtered_LengthvsQualityScatterPlot_dot.pdf",
        "analysis/sample1/paired/spades-default/spades/quast/report.html",
        "analysis/sample2/paired/spades-default/spades/quast/report.html",
        "analysis/sample3/pacbio-hifi/hicanu/canu/quast/report.html",
        "analysis/sample4/nano-hq/flye_ONT/flye/quast/report.html",
    ]
    assert observed == expected
