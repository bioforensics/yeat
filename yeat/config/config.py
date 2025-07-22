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


REQUIRED_KEYS = {"samples", "assemblers"}
OPTIONAL_KEYS = {
    "coverage_depth": 150,
    "downsample": -1,  # -1 disable, 0 auto
    "genome_size": 0,  # 0 auto
    "min_length": 100,
    "quality": 10,
    "skip_filter": False,
}


class AssemblyConfiguration(BaseModel):
    global_settings: Dict
    samples: Dict
    assemblers: Dict

    @classmethod
    def parse_snakemake_config(cls, config):
        keys = config["config"].keys()
        cls._check_required_keys(keys)
        cls._check_optional_keys(keys)
        global_settings = cls._parse_global_settings(config["config"])
        samples = cls._parse_samples(config["config"], global_settings)
        assemblers = cls._parse_assemblers(config["config"], samples)
        return cls(global_settings=global_settings, samples=samples, assemblers=assemblers)

    @staticmethod
    def _check_required_keys(keys):
        intersection = list(keys & REQUIRED_KEYS)
        if not intersection:
            raise ConfigurationError(f"YEAT configuration must include {REQUIRED_KEYS}")

    @staticmethod
    def _check_optional_keys(keys):
        valid_keys = set(OPTIONAL_KEYS.keys()).union(REQUIRED_KEYS)
        invalid_keys = list(set(keys).difference(valid_keys))
        if len(invalid_keys) > 0:
            raise ConfigurationError(f"YEAT configuration has unrecongizable keys {invalid_keys}")

    @staticmethod
    def _parse_global_settings(config):
        global_settings = defaultdict(lambda: None)
        for key, value in OPTIONAL_KEYS.items():
            if key in config:
                if type(config[key]) != type(value):
                    raise ConfigurationError("wrong data type for [{key}]")
                global_settings[key] = config[key]
                continue
            global_settings[key] = value
        return global_settings

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
            assembler_class = select(data["algorithm"])
            assemblers[label] = assembler_class.parse_data(label, data, samples)
        return assemblers

    @property
    def targets(self):
        targets = list()
        for sample in self.samples.values():
            targets.extend(sample.targets)
        for assembler in self.assemblers.values():
            targets.extend(assembler.targets)
        return targets


class ConfigurationError(ValueError):
    pass
