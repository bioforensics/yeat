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


ASSEMBLY_ALGORITHMS = ["spades", "megahit", "unicycler"]


class AssemblerConfigError(ValueError):
    pass


class AssemblerConfig:
    def __init__(self, assembler, extra_args=""):
        self.assembler = assembler
        self.extra_args = extra_args

    @classmethod
    def from_json(cls, data):
        return cls(data["assembler"], data["extra_args"])

    @staticmethod
    def parse_json(instream):
        data = json.load(instream)
        algorithms = set()
        assemblers = []
        for d in data:
            AssemblerConfig.validate_config(d)
            algorithm = d["assembler"]
            AssemblerConfig.check_algorithm(algorithm, algorithms)
            algorithms.add(algorithm)
            assemblers.append(AssemblerConfig.from_json(d))
        return assemblers

    @staticmethod
    def check_algorithm(algorithm, algorithms):
        if algorithm not in ASSEMBLY_ALGORITHMS:
            message = f"Found unsupported assembly algorithm in config settings: [[{algorithm}]]!"
            raise ValueError(message)
        if algorithm in algorithms:
            message = f"Found duplicate assembly algorithm in config settings: [[{algorithm}]]!"
            raise ValueError(message)

    @staticmethod
    def validate_config(config):
        expectedkeys = ("assembler", "extra_args")
        missingkeys = set()
        extrakeys = set()
        for key in expectedkeys:
            if key not in config:
                missingkeys.add(key)
        for key in config:
            if key not in expectedkeys:
                extrakeys.add(key)
        if len(missingkeys) > 0:
            keystr = ",".join(sorted(missingkeys))
            message = f"Missing assembly configuration setting(s): [[{keystr}]]!"
            raise AssemblerConfigError(message)
        if len(extrakeys) > 0:
            keystr = ",".join(sorted(extrakeys))
            message = f"Ignoring unsupported configuration key(s): [[{keystr}]]!"
            warn(message)
