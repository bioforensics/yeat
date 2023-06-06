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
from warnings import warn


ALGORITHMS = ("spades", "megahit", "unicycler", "flye", "canu")
KEYS1 = ("samples", "assemblers")
KEYS2 = ("label", "algorithm", "extra_args", "samples")


class AssemblyConfigurationError(ValueError):
    pass


class AssemblerConfig:
    def __init__(self, samples, assembly_configs):
        self.samples = {k: v.sample for k, v in samples.items()}
        self.labels = [config.label for config in assembly_configs]
        self.assemblers = {config.label: config.algorithm for config in assembly_configs}
        self.extra_args = {config.label: config.extra_args for config in assembly_configs}
        self.label_to_samples = {config.label: config.samples for config in assembly_configs}

        # paired_configs = []
        # pacbio_configs = []
        # for assembly in assembly_configs:
        #     if assembly.algorithm in PAIRED:
        #         paired_configs.append(assembly)
        #     elif assembly.algorithm in PACBIO:
        #         pacbio_configs.append(assembly)

    @classmethod
    def from_json(cls, instream):
        data = json.load(instream)
        print(data)
        assert 0
        samples = []
        assemblers = []
        config = cls(samples, assemblers)
        return config

    def validate():
        print("in this function")
        pass

    def check_keys(data, keys):
        missingkeys = set(keys) - set(data.keys())
        extrakeys = set(data.keys()) - set(keys)
        if len(missingkeys) > 0:
            keystr = ",".join(sorted(missingkeys))
            message = f"Missing assembly configuration setting(s) '{keystr}'"
            raise AssemblyConfigurationError(message)
        if len(extrakeys) > 0:
            keystr = ",".join(sorted(extrakeys))
            message = f"Ignoring unsupported configuration key(s) '{keystr}'"
            warn(message)


#     @staticmethod
#     def parse_json(instream):
#         configdata = json.load(instream)
#         AssemblerConfig.validate(configdata, KEYS1)
#         for assembler in configdata["assemblers"]:
#             AssemblerConfig.validate(assembler, KEYS2)
#         labels = [assembler["label"] for assembler in configdata["assemblers"]]
#         if len(labels) > len(set(labels)):
#             message = "Duplicate assembly labels: please check config file"
#             raise AssemblyConfigurationError(message)
#         sampledict = {}
#         for key, value in configdata["samples"].items():
#             sampledict[key] = Sample.from_json(value)
#         assemblerlist = [Assembler.from_json(assembler) for assembler in configdata["assemblers"]]
#         return sampledict, assemblerlist


class Sample:
    def __init__(self, data):
        sample = []
        for fastq in data:
            read = Path(fastq).resolve()
            if not read.is_file():
                raise FileNotFoundError(f"No such file: '{read}'")
            if str(read) in sample:
                message = f"Found duplicate read sample: '{read}'"
                raise AssemblyConfigurationError(message)
            else:
                sample.append(str(read))
        self.sample = sample

    @classmethod
    def from_json(cls, data):
        return cls(data)


class Assembler:
    def __init__(self, label, algorithm, samples, extra_args=""):
        self.label = label
        if algorithm not in ALGORITHMS:
            raise AssemblyConfigurationError(f"Unsupported assembly algorithm '{algorithm}'")
        self.algorithm = algorithm
        self.samples = samples
        self.extra_args = extra_args

    @classmethod
    def from_json(cls, data):
        return cls(data["label"], data["algorithm"], data["samples"], data["extra_args"])
