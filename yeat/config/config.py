# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .assemblers import select
from .sample import Sample
from collections import defaultdict
from pydantic import BaseModel
from typing import Dict


QC_DEFUALT_VALUES = {
    "coverage_depth": 150,
    "downsample": -1,
    "genome_size": 0,
    "min_length": 100,
    "quality": 10,
    "skip_filter": False,
}


class AssemblyConfiguration(BaseModel):
    flags: Dict
    samples: Dict
    assemblers: Dict

    @classmethod
    def parse_snakemake_config(cls, config):
        keys = config["config"].keys()
        cls._check_required_keys(keys)
        cls._check_optional_keys(keys)
        flags = cls._parse_flags(config["config"])  # need to do value type checking
        samples = cls._parse_samples(config, flags)
        assemblers = cls._parse_assemblers(config, samples)
        return cls(flags=flags, samples=samples, assemblers=assemblers)

    @staticmethod
    def _check_required_keys(keys):
        if "samples" not in keys:
            raise ConfigurationError("YEAT configuration must include [samples]")
        if "assemblers" not in keys:
            raise ConfigurationError("YEAT configuration must include [assemblers]")

    @staticmethod
    def _check_optional_keys(keys):
        valid_keys = set(QC_DEFUALT_VALUES.keys()).union({"samples", "assemblers"})
        elements_only_in_list1 = list(set(keys).difference(valid_keys))
        if len(elements_only_in_list1) > 0:
            raise (ConfigurationError("found unrecongizable keys!"))

    @staticmethod
    def _parse_flags(config):
        flags = defaultdict(lambda: None)
        for key, value in QC_DEFUALT_VALUES.items():
            if key in config:
                flags[key] = config[key]
                continue
            flags[key] = value
        return flags

    @staticmethod
    def _parse_samples(config, flags):
        samples = dict()
        for label, sample_data in config["config"]["samples"].items():
            samples[label] = Sample.parse_data(label, sample_data, flags)
        return samples

    @staticmethod
    def _parse_assemblers(config, samples):
        assemblers = dict()
        for label, assembler_data in config["config"]["assemblers"].items():
            assembler_class = select(assembler_data["algorithm"])
            assemblers[label] = assembler_class.parse_data(label, assembler_data, samples)
        return assemblers

    @property
    def rule_all_targets(self):
        targets = list()
        for sample in self.samples.values():
            targets.extend(sample.target_files)
        for assembler in self.assemblers.values():
            targets.extend(assembler.target_files)
        return targets


class ConfigurationError(ValueError):
    pass
