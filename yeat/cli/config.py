# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import json
from warnings import warn


ALGORITHMS = ("spades", "megahit", "unicycler", "flye", "canu")
KEYS = ["label", "algorithm", "extra_args"]


class AssemblyConfigurationError(ValueError):
    pass


class AssemblerConfig:
    def __init__(self, label, algorithm, extra_args=""):
        self.label = label
        if algorithm not in ALGORITHMS:
            raise AssemblyConfigurationError(f"Unsupported assembly algorithm '{algorithm}'")
        self.algorithm = algorithm
        self.extra_args = extra_args

    @classmethod
    def from_json(cls, data):
        return cls(data["label"], data["algorithm"], data["extra_args"])

    @staticmethod
    def parse_json(instream):
        configdata = json.load(instream)
        for entry in configdata:
            AssemblerConfig.validate(entry)
        labels = [entry["label"] for entry in configdata]
        if len(labels) > len(set(labels)):
            message = "Duplicate assembly labels: please check config file"
            raise AssemblyConfigurationError(message)
        configlist = [AssemblerConfig.from_json(entry) for entry in configdata]
        return configlist

    @staticmethod
    def validate(config):
        missingkeys = set(KEYS) - set(config.keys())
        extrakeys = set(config.keys()) - set(KEYS)
        if len(missingkeys) > 0:
            keystr = ",".join(sorted(missingkeys))
            message = f"Missing assembly configuration setting(s) '{keystr}'"
            raise AssemblyConfigurationError(message)
        if len(extrakeys) > 0:
            keystr = ",".join(sorted(extrakeys))
            message = f"Ignoring unsupported configuration key(s) '{keystr}'"
            warn(message)
