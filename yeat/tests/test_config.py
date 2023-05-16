# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import json
from pathlib import Path
import pytest
from yeat.cli.config import (
    Assembler,
    AssemblerConfig,
    AssemblyConfigurationError,
    Sample,
    KEYS1,
    KEYS2,
)
from yeat.tests import data_file


def test_unsupported_assembly_algorithm():
    algorithm = "unsupported_algorithm"
    pattern = rf"Unsupported assembly algorithm '{algorithm}'"
    with pytest.raises(ValueError, match=pattern):
        Assembler("label1", algorithm, ["sample1"])


def test_duplicate_assembly_labels(tmp_path):
    wd = str(tmp_path)
    data = json.load(open(data_file("configs/paired.cfg")))
    data["assemblers"].append(data["assemblers"][0])
    print(data["assemblers"])
    cfg = str(Path(wd).resolve() / "paired.cfg")
    json.dump(data, open(cfg, "w"))
    pattern = r"Duplicate assembly labels: please check config file"
    with pytest.raises(ValueError, match=pattern):
        AssemblerConfig.parse_json(open(cfg))


def test_parse_json():
    f = open(data_file("configs/paired.cfg"))
    samples, algorithms = AssemblerConfig.parse_json(f)
    for sample_name, reads in samples.items():
        assert len(reads.sample) == 2
    assemblers = [assembler.algorithm for assembler in algorithms]
    assert assemblers == ["spades", "megahit", "unicycler"]


def test_valid_config_entry():
    data = json.load(open(data_file("configs/paired.cfg")))
    AssemblerConfig.validate(data, KEYS1)
    for assembler in data["assemblers"]:
        AssemblerConfig.validate(assembler, KEYS2)


@pytest.mark.parametrize("key,", ["label", "algorithm", "extra_args", "samples"])
def test_missing_key_in_config_entry(key):
    data = json.load(open(data_file("configs/paired.cfg")))
    del data["assemblers"][0][key]
    pattern = rf"Missing assembly configuration setting\(s\) '{key}'"
    with pytest.raises(AssemblyConfigurationError, match=pattern):
        AssemblerConfig.validate(data["assemblers"][0], KEYS2)


def test_unsupported_key_in_config_entry():
    data = json.load(open(data_file("configs/paired.cfg")))
    data["assemblers"][0]["not"] = "supported"
    pattern = r"Ignoring unsupported configuration key\(s\) 'not'"
    with pytest.warns(match=pattern):
        AssemblerConfig.validate(data["assemblers"][0], KEYS2)


@pytest.mark.parametrize(
    "reads,badfile",
    [
        (["nonexistant/read1/file", "nonexistant/read2/file"], 0),
        ([data_file("short_reads_1.fastq.gz"), "nonexistant/read2/file"], 1),
        (["nonexistant/read1/file", data_file("short_reads_2.fastq.gz")], 0),
    ],
)
def test_sample_read_file_not_found(reads, badfile):
    pattern = rf"No such file: '.*{reads[badfile]}'"
    with pytest.raises(FileNotFoundError, match=pattern):
        Sample(reads)


def test_sample_with_duplicate_reads():
    reads = [data_file("short_reads_1.fastq.gz"), data_file("short_reads_1.fastq.gz")]
    pattern = rf"Found duplicate read sample: '.*short_reads_1.fastq.gz'"
    with pytest.raises(AssemblyConfigurationError, match=pattern):
        Sample(reads)
