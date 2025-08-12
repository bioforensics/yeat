# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .assemblers import ALGORITHM_CONFIGS
from .assemblers.assembler import Assembler
from .global_settings import GlobalSettings
from .sample import Sample
from pydantic import BaseModel, field_validator
from typing import Dict


class AssemblyConfiguration(BaseModel):
    global_settings: GlobalSettings
    samples: Dict[str, Sample]
    assemblers: Dict[str, Assembler]

    @field_validator("samples")
    @classmethod
    def has_one_sample(cls, samples):
        if not samples:
            raise ConfigurationError("Config has no samples")
        return samples

    @field_validator("assemblers")
    @classmethod
    def has_one_assembler(cls, assemblers):
        if not assemblers:
            raise ConfigurationError("Config has no assemblers")
        return assemblers

    @classmethod
    def parse_snakemake_config(cls, config):
        global_settings = cls._parse_global_settings(config)
        samples = cls._parse_samples(config, global_settings)
        assemblers = cls._parse_assemblers(config, samples)
        return cls(global_settings=global_settings, samples=samples, assemblers=assemblers)

    @staticmethod
    def _parse_global_settings(config):
        data = config.get("global_settings", {})
        return GlobalSettings.parse_data(data)

    @staticmethod
    def _parse_samples(config, global_settings):
        samples = dict()
        for label, data in config["samples"].items():
            samples[label] = Sample.parse_data(label, data, global_settings)
        return samples

    @staticmethod
    def _parse_assemblers(config, samples):
        assemblers = dict()
        for label, data in config["assemblers"].items():
            assembler_class = AssemblyConfiguration.select(data["algorithm"])
            assemblers[label] = assembler_class.parse_data(label, data, samples)
        return assemblers

    @classmethod
    def select(self, algorithm):
        if algorithm not in ALGORITHM_CONFIGS:
            raise ConfigurationError(f"Unknown assembly algorithm {algorithm}")
        return ALGORITHM_CONFIGS[algorithm]

    @property
    def targets(self):
        targets = list()
        for sample in self.samples.values():
            targets.extend(sample.targets)
        for assembler in self.assemblers.values():
            targets.extend(assembler.targets)
        return targets

    def get_sample_input_files(self, sample, read_type):
        return self.samples[sample].data[read_type]

    def get_sample_skip_filter(self, sample):
        return self.samples[sample].skip_filter

    def get_sample_quality(self, sample):
        return self.samples[sample].quality

    def get_sample_min_length(self, sample):
        return self.samples[sample].min_length

    def get_sample_downsample(self, sample):
        return self.samples[sample].downsample

    def get_sample_genome_size(self, sample):
        return self.samples[sample].genome_size

    def get_sample_coverage_depth(self, sample):
        return self.samples[sample].coverage_depth

    def get_assembler_input_files(self, label, sample):
        return self.assemblers[label].input_files(sample)

    def get_assembler_input_args(self, label, sample):
        return self.assemblers[label].input_args(sample)

    def get_assembler_extra_args(self, label):
        return self.assemblers[label].extra_args

    def get_assembler_bowtie2_input_args(self, label, sample):
        return self.assemblers[label].bowtie2_input_args(sample)


class ConfigurationError(ValueError):
    pass
