# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import READ_TYPES, AssemblyConfigError
from .assembly import Assembly
from .sample import Sample
from itertools import chain


CONFIG_KEYS = ("samples", "assemblies")
DOWNSAMPLE_KEYS = ("downsample", "coverage_depth", "genome_size")
SAMPLE_KEYS = READ_TYPES + DOWNSAMPLE_KEYS
ASSEMBLY_KEYS = ("algorithm", "extra_args", "samples", "mode")


class AssemblyConfig:
    def __init__(self, config, threads=1, bandage=False):
        self.config = config
        self.validate_config_keys()
        self.threads = threads
        self.bandage = bandage
        self.samples = self.create_sample_objects()
        self.assemblies = self.create_assembly_objects()
        self.target_files = self.get_target_files()

    def validate_config_keys(self):
        self.check_required_keys(self.config.keys(), CONFIG_KEYS)
        for sample in self.config["samples"].values():
            self.check_valid_keys(sample.keys(), SAMPLE_KEYS)
        for assembly in self.config["assemblies"].values():
            self.check_required_keys(assembly.keys(), ASSEMBLY_KEYS)

    def check_required_keys(self, observed_keys, expected_keys):
        missing_keys = set(expected_keys) - set(observed_keys)
        if missing_keys:
            key_str = ",".join(sorted(missing_keys))
            message = f"Missing assembly configuration setting(s) '{key_str}'"
            raise AssemblyConfigError(message)
        self.check_valid_keys(observed_keys, expected_keys)

    def check_valid_keys(self, observed_keys, expected_keys):
        extra_keys = set(observed_keys) - set(expected_keys)
        if extra_keys:
            key_str = ",".join(sorted(extra_keys))
            message = f"Found unsupported configuration key(s) '{key_str}'"
            raise AssemblyConfigError(message)

    def create_sample_objects(self):
        samples = {}
        for label, sample in self.config["samples"].items():
            samples[label] = Sample(label, sample)
        return samples

    def create_assembly_objects(self):
        assemblies = {}
        for label, assembly in self.config["assemblies"].items():
            assembly["samples"] = self.get_sample_objects(assembly["samples"])
            assemblies[label] = Assembly(label, assembly, self.threads, self.bandage)
        return assemblies

    def get_sample_objects(self, samples):
        return dict(((sample, self.samples[sample]) for sample in samples))

    def get_target_files(self):
        target_files = []
        for element in chain(self.samples.values(), self.assemblies.values()):
            target_files += element.target_files
        return target_files
