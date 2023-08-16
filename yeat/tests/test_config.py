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
from yeat import cli
from yeat.cli.config import Assembler, AssemblerConfig, AssemblyConfigurationError, Sample
from yeat.tests import data_file


def test_unsupported_assembly_algorithm():
    assembler = {
        "label": "unsuported_algorithm",
        "algorithm": "unsupported_alogrithm",
        "extra_args": "",
        "samples": ["sample1"],
    }
    pattern = rf"Unsupported assembly algorithm '{assembler['algorithm']}'"
    with pytest.raises(ValueError, match=pattern):
        Assembler(assembler, 1)


def test_duplicate_assembly_labels(tmp_path):
    wd = str(tmp_path)
    data = json.load(open(data_file("configs/paired.cfg")))
    data["assemblers"].append(data["assemblers"][0])
    cfg = str(Path(wd).resolve() / "paired.cfg")
    json.dump(data, open(cfg, "w"))
    pattern = r"Duplicate assembly labels: please check config file"
    with pytest.raises(ValueError, match=pattern):
        AssemblerConfig.from_json(cfg, 1)


def test_valid_config():
    cfg = data_file("configs/paired.cfg")
    config = AssemblerConfig.from_json(cfg, 1)
    assert len(config.samples) == 2
    assemblers = [assembler.algorithm for assembler in config.assemblers]
    assert assemblers == ["spades", "megahit", "unicycler"]


@pytest.mark.parametrize("key,", ["label", "algorithm", "extra_args", "samples"])
def test_missing_key_in_config_entry(key):
    data = json.load(open(data_file("configs/paired.cfg")))
    del data["assemblers"][0][key]
    pattern = rf"Missing assembly configuration setting\(s\) '{key}'"
    with pytest.raises(AssemblyConfigurationError, match=pattern):
        AssemblerConfig(data, 1)


def test_unsupported_key_in_config_entry():
    data = json.load(open(data_file("configs/paired.cfg")))
    data["assemblers"][0]["not"] = "supported"
    pattern = r"Ignoring unsupported configuration key\(s\) 'not'"
    with pytest.warns(match=pattern):
        AssemblerConfig(data, 1)


@pytest.mark.parametrize(
    "reads,badfile",
    [
        (["nonexistant/read1/file", "nonexistant/read2/file"], 0),
        ([data_file("short_reads_1.fastq.gz"), "nonexistant/read2/file"], 1),
        (["nonexistant/read1/file", data_file("short_reads_2.fastq.gz")], 0),
    ],
)
def test_sample_read_file_not_found(reads, badfile):
    sample = {"paired": reads}
    pattern = rf"No such file: '.*{reads[badfile]}'"
    with pytest.raises(FileNotFoundError, match=pattern):
        Sample(sample)


def test_sample_with_duplicate_reads():
    sample = {"paired": [data_file("short_reads_1.fastq.gz"), data_file("short_reads_1.fastq.gz")]}
    pattern = rf"Found duplicate read sample: '.*short_reads_1.fastq.gz'"
    with pytest.raises(AssemblyConfigurationError, match=pattern):
        Sample(sample)


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
    assembler = {
        "label": "label1",
        "algorithm": "canu",
        "extra_args": extra_args,
        "samples": ["sample1"],
    }
    with pytest.raises(ValueError, match=expected):
        Assembler(assembler, cores)


# @pytest.mark.parametrize(
#     "cfg,readtype,subsamples,sublabels",
#     [
#         (
#             data_file("configs/flye_unicycler.cfg"),
#             "all",
#             ["sample1", "sample2"],
#             ["flye-default", "spades-default"],
#         ),
#         (data_file("configs/flye_unicycler.cfg"), "pacbio", ["sample1"], ["flye-default"]),
#         (data_file("configs/flye_unicycler.cfg"), "paired", ["sample2"], ["spades-default"]),
#     ],
# )
# def test_to_dict(cfg, readtype, subsamples, sublabels):
#     args = cli.get_parser().parse_args([cfg])
#     config = AssemblerConfig.from_json(args.config, args.threads)
#     observed = config.to_dict(args, readtype)
#     for sample in subsamples:
#         assert sample in observed["samples"]
#     for label in sublabels:
#         assert label in observed["labels"]
#         assert label in observed["assemblers"]
#         assert observed["assemblers"][label] in label
#     assert len(observed["samples"]) == len(subsamples)
#     assert len(observed["labels"]) == len(sublabels)
#     assert len(observed["assemblers"]) == len(sublabels)


# def test_multiple_readtypes_in_sample():
#     data = json.load(open(data_file("configs/ont.cfg")))
#     data["samples"]["sample1"]["extra_readtype"] = ["long_read.fastq"]
#     pattern = r"Multiple read types in sample 'sample1'"
#     with pytest.raises(ValueError, match=pattern):
#         AssemblerConfig(data, 1)


def test_unsupported_readtype_in_sample():
    data = json.load(open(data_file("configs/ont.cfg")))
    del data["samples"]["Ecoli_K12_MG1655_R10.3_HAC"]["nano-hq"]
    data["samples"]["Ecoli_K12_MG1655_R10.3_HAC"]["not"] = ["supported"]
    pattern = r"Unsupported read type 'not'"
    with pytest.raises(ValueError, match=pattern):
        AssemblerConfig(data, 1)


# def test_batch():
#     data = json.load(open(data_file("configs/all_assemblers.cfg")))
#     config = AssemblerConfig(data, 4)
#     paired_samples = set(config.batch["paired"]["samples"].keys())
#     paired_algorithms = [assembler.algorithm for assembler in config.batch["paired"]["assemblers"]]
#     assert paired_samples == {"sample1", "sample2"}
#     assert paired_algorithms == [
#         "spades",
#         "spades",
#         "megahit",
#         "megahit",
#         "unicycler",
#         "unicycler",
#     ]
#     pacbio_samples = set(config.batch["pacbio"]["samples"].keys())
#     pacbio_algorithms = [assembler.algorithm for assembler in config.batch["pacbio"]["assemblers"]]
#     assert pacbio_samples == {"sample3"}
#     assert pacbio_algorithms == ["canu", "flye"]
#     oxford_samples = set(config.batch["oxford"]["samples"].keys())
#     oxford_algorithms = [assembler.algorithm for assembler in config.batch["oxford"]["assemblers"]]
#     assert oxford_samples == {"sample4"}
#     assert oxford_algorithms == ["canu", "flye"]
