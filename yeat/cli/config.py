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
KEYS1 = ["samples", "assemblers"]
KEYS2 = ["label", "algorithm", "extra_args", "samples"]


class AssemblyConfigurationError(ValueError):
    pass


class AssemblerConfig:
    @staticmethod
    def parse_json(instream):
        configdata = json.load(instream)
        AssemblerConfig.validate(configdata, KEYS1)
        for assembler in configdata["assemblers"]:
            AssemblerConfig.validate(assembler, KEYS2)
        samples = [sample for sample in configdata["samples"]]
        if len(samples) > len(set(samples)):
            message = "Duplicate sample names: please check config file"
            raise AssemblyConfigurationError(message)
        labels = [assembler["label"] for assembler in configdata["assemblers"]]
        if len(labels) > len(set(labels)):
            message = "Duplicate assembly labels: please check config file"
            raise AssemblyConfigurationError(message)
        sampledict = {}
        for key, value in configdata["samples"].items():
            sampledict[key] = Sample.from_json(value)
        assemblerlist = [Assembler.from_json(assembler) for assembler in configdata["assemblers"]]
        return sampledict, assemblerlist

    @staticmethod
    def validate(config, keystemp):
        missingkeys = set(keystemp) - set(config.keys())
        extrakeys = set(config.keys()) - set(keystemp)
        if len(missingkeys) > 0:
            keystr = ",".join(sorted(missingkeys))
            message = f"Missing assembly configuration setting(s) '{keystr}'"
            raise AssemblyConfigurationError(message)
        if len(extrakeys) > 0:
            keystr = ",".join(sorted(extrakeys))
            message = f"Ignoring unsupported configuration key(s) '{keystr}'"
            warn(message)


class Sample:
    def __init__(self, data):
        sample = []
        for fastq in data:
            read = Path(fastq).resolve()
            if not read.is_file():
                raise FileNotFoundError(f"No such file: '{read}'")
            if str(read) in sample:
                message = f"Found duplicate read sample: `{read}`"
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


# test for not enough samples. for example, assembler wants sample1 and sample2 but user didn't put in sample2 in
# sample section
