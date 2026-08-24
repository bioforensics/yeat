# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import SAMPLES
from pathlib import Path
import pytest
from yeat.config.assemblers import SPAdesAssembler, PenguiNAssembler
from yeat.config.config import ConfigurationError, AssemblyConfiguration
from yeat.config.global_settings import GlobalSettings
from yeat.tests import data_file
from yeat.workflow import get_config_data


@pytest.mark.parametrize("samples", [{"sample1": SAMPLES["sample1"]}, SAMPLES])
def test_has_one_sample(samples):
    AssemblyConfiguration.has_one_sample(samples)


def test_has_no_sample():
    message = "Config has no samples"
    with pytest.raises(ConfigurationError, match=message):
        AssemblyConfiguration.has_one_sample({})


def test_has_one_assembler():
    AssemblyConfiguration.has_one_assembler({"spades"})


def test_has_no_assembler():
    message = "Config has no assemblers"
    with pytest.raises(ConfigurationError, match=message):
        AssemblyConfiguration.has_one_assembler({})


def test_parse_snakemake_config():
    config = {
        "global_settings": {"filter": {"enabled": False}},
        "samples": {"sample1": {"illumina": ["READ1.fastq.gz", "READ2.fastq.gz"]}},
        "assemblers": {"spades_default": {"algorithm": "spades"}},
    }
    AssemblyConfiguration.parse_snakemake_config(config)


def test_select():
    AssemblyConfiguration.select("spades")


def test_select_algorithm_not_supported():
    message = "Unknown assembly algorithm DNE"
    with pytest.raises(ConfigurationError, match=message):
        AssemblyConfiguration.select("DNE")


def test_targets():
    global_settings = GlobalSettings(filter={}, downsample={})
    samples = {"sample1": SAMPLES["sample1"]}
    assembler = {
        "spades_default": SPAdesAssembler(
            label="spades_default", samples={"sample1": SAMPLES["sample1"]}
        )
    }
    config = AssemblyConfiguration(
        global_settings=global_settings, samples=samples, assemblers=assembler
    )
    assert config.targets == [
        "analysis/sample1/qc/illumina/fastqc/R1_fastqc.html",
        "analysis/sample1/qc/illumina/fastqc/R2_fastqc.html",
        "analysis/sample1/yeat/spades/spades_default/quast/report.html",
        "analysis/sample1/yeat/spades/spades_default/bandage/.done",
    ]


def test_spades_metadata():
    global_settings = GlobalSettings(filter={}, downsample={})
    samples = {"sample1": SAMPLES["sample1"]}
    assembler = {
        "spades_default": SPAdesAssembler(
            label="spades_default", samples={"sample1": SAMPLES["sample1"]}
        )
    }
    config = AssemblyConfiguration(
        global_settings=global_settings, samples=samples, assemblers=assembler
    )
    assert config.get_sample_input_files("sample1", "illumina") == [
        Path("READ1.fastq.gz"),
        Path("READ2.fastq.gz"),
    ]
    assert config.get_sample_filter_enabled("sample1", "short") == False
    assert (
        config.get_sample_filter_args("sample1", "short")
        == "--length_required 50 --detect_adapter_for_pe"
    )
    assert config.get_sample_downsample_enabled("sample1", "short") == False
    assert config.get_sample_downsample_method("sample1", "short") == "random"
    assert config.get_sample_target_depth("sample1", "short") == 150
    assert config.get_sample_target_num_reads("sample1", "short") == "auto"
    assert config.get_sample_genome_size("sample1", "short") == "auto"
    assert config.get_assembler_input_files("spades_default", "sample1") == [
        "analysis/sample1/qc/illumina/downsample/R1.fastq.gz",
        "analysis/sample1/qc/illumina/downsample/R2.fastq.gz",
    ]
    assert (
        config.get_assembler_input_args("spades_default", "sample1")
        == "-1 analysis/sample1/qc/illumina/downsample/R1.fastq.gz -2 analysis/sample1/qc/illumina/downsample/R2.fastq.gz"
    )
    assert config.get_assembler_extra_args("spades_default") == ""


def test_penguin_metadata():
    global_settings = GlobalSettings(filter={}, downsample={})
    samples = {"sample1": SAMPLES["sample1"]}
    assembler = {
        "penguin_default": PenguiNAssembler(
            label="penguin_default", samples={"sample1": SAMPLES["sample1"]}
        )
    }
    config = AssemblyConfiguration(
        global_settings=global_settings, samples=samples, assemblers=assembler
    )
    assert (
        config.get_assembler_bowtie2_input_args("penguin_default", "sample1")
        == "-1 analysis/sample1/qc/illumina/downsample/R1.fastq.gz -2 analysis/sample1/qc/illumina/downsample/R2.fastq.gz"
    )


def test_overwrite_global_settings():
    data = get_config_data(data_file("configs/overwrite_global_settings.toml"))
    config = AssemblyConfiguration.parse_snakemake_config(data)
    assert config.global_settings.filter.short_filter_settings.enabled == False
    assert config.global_settings.downsample.short_downsample_settings.enabled == False
    assert config.global_settings.downsample.short_downsample_settings.genome_size == "auto"
    assert config.samples["Animal_289"].filter.short_filter_settings.enabled == False
    assert config.samples["Animal_289"].downsample.short_downsample_settings.enabled == False
    assert config.samples["Animal_289"].downsample.short_downsample_settings.genome_size == "auto"
    assert config.samples["short_reads"].filter.short_filter_settings.enabled == True
    assert config.samples["short_reads"].downsample.short_downsample_settings.enabled == True
    assert config.samples["short_reads"].downsample.short_downsample_settings.genome_size == 15000
