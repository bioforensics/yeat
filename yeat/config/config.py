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


BASE_KEYS = ("samples", "assemblies")
ASSEMBLY_KEYS = ("algorithm", "extra_args", "samples", "mode")


class AssemblyConfig:
    def __init__(self, data, threads):
        self.data = data
        self.validate()
        self.threads = threads
        self.create_sample_and_assembly_objects()
        # need to do another validation checking if the assembly object's mode has
        # samples that have the correct reads in each of them.

    def validate(self):
        self.check_required_keys(self.data.keys(), BASE_KEYS)
        for key, value in self.data["samples"].items():
            self.check_valid_keys(value.keys(), READ_TYPES)
        for key, value in self.data["assemblies"].items():
            self.check_required_keys(value.keys(), ASSEMBLY_KEYS)

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

    def create_sample_and_assembly_objects(self):
        self.samples = {}
        self.assemblies = {}
        for key, value in self.data["samples"].items():
            self.samples[key] = Sample(key, value)
        for key, value in self.data["assemblies"].items():
            self.assemblies[key] = Assembly(key, value, self.threads)
