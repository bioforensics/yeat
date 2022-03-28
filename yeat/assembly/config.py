# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import json


ASSEMBLY_ALGORITHMS = ["spades"]


class AssemblyConfigError(ValueError):
    pass


class AssemblyConfiguration:
    def __init__(self, label, algorithm):
        self.label = label
        self.algorithm = algorithm

    @classmethod
    def from_json(cls, d):
        return cls(d["label"], d["algorithm"])

    @staticmethod
    def parse_json(fh):
        algorithms = []
        assemblers = []
        data = json.load(fh)
        for d in data:
            algorithm = d["algorithm"]
            if algorithm not in ASSEMBLY_ALGORITHMS:
                message = f"Found unsupported assembly algorithm in config file: [[{algorithm}]]!"
                raise AssemblyConfigError(message)
            if algorithm in algorithms:
                message = f"Found duplicate assembly algorithm in config file: [[{algorithm}]]!"
                raise AssemblyConfigError(message)
            algorithms.append(algorithm)
            assemblers.append(AssemblyConfiguration.from_json(d))
        return assemblers
