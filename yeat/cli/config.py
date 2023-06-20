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


PAIRED = ("spades", "megahit", "unicycler")
PACBIO = ("canu", "flye")
ALGORITHMS = PAIRED + PACBIO


class AssemblyConfigurationError(ValueError):
    pass


class AssemblerConfig:
    def __init__(self, data, threads):
        self.data = data
        self.validate()
        self.threads = threads
        self.create_sample_and_assembler_objects()
        self.batch()

    @classmethod
    def from_json(cls, infile, threads):
        data = json.load(open(infile))
        return cls(data, threads)

    def validate(self):
        self.check_keys(self.data, ("samples", "assemblers"))
        for assembler in self.data["assemblers"]:
            self.check_keys(assembler, ("label", "algorithm", "extra_args", "samples"))
        labels = [assembler["label"] for assembler in self.data["assemblers"]]
        if len(labels) > len(set(labels)):
            message = "Duplicate assembly labels: please check config file"
            raise AssemblyConfigurationError(message)

    def check_keys(self, data, keys):
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

    def create_sample_and_assembler_objects(self):
        self.samples = {}
        for key, value in self.data["samples"].items():
            self.samples[key] = Sample(value)
        self.assemblers = [
            Assembler.from_data(assembler, self.threads) for assembler in self.data["assemblers"]
        ]

    def batch(self):
        paired_assemblers = []
        pacbio_assemblers = []
        for assembler in self.assemblers:
            if assembler.algorithm in PAIRED:
                paired_assemblers.append(assembler)
            elif assembler.algorithm in PACBIO:
                pacbio_assemblers.append(assembler)
        self.batch = {
            "paired": {
                "samples": self.get_batch_samples(paired_assemblers),
                "assemblers": paired_assemblers,
            },
            "pacbio": {
                "samples": self.get_batch_samples(pacbio_assemblers),
                "assemblers": pacbio_assemblers,
            },
        }

    def get_batch_samples(self, assemblers):
        samples = {}
        for assembler in assemblers:
            samples = samples | dict(
                (key, self.samples[key]) for key in assembler.samples if key in self.samples
            )
        return samples

    def to_dict(self, args, readtype="all"):
        if readtype == "all":
            samples = self.samples
            assemblers = self.assemblers
        else:
            samples = self.batch[readtype]["samples"]
            assemblers = self.batch[readtype]["assemblers"]
        return dict(
            samples={key: value.sample for key, value in samples.items()},
            labels=[assembler.label for assembler in assemblers],
            assemblers={assembler.label: assembler.algorithm for assembler in assemblers},
            extra_args={assembler.label: assembler.extra_args for assembler in assemblers},
            label_to_samples={assembler.label: assembler.samples for assembler in assemblers},
            threads=args.threads,
            downsample=args.downsample,
            coverage=args.coverage,
            genomesize=args.genome_size,
            seed=args.seed,
        )


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
            sample.append(str(read))
        self.sample = sample


class Assembler:
    def __init__(self, label, algorithm, samples, extra_args, threads):
        self.label = label
        if algorithm not in ALGORITHMS:
            raise AssemblyConfigurationError(f"Unsupported assembly algorithm '{algorithm}'")
        self.algorithm = algorithm
        self.samples = samples
        self.extra_args = extra_args
        self.threads = threads
        if algorithm == "canu":
            self.check_canu_required_params()

    @classmethod
    def from_data(cls, data, threads):
        return cls(data["label"], data["algorithm"], data["samples"], data["extra_args"], threads)

    def check_canu_required_params(self):
        if "genomeSize=" not in self.extra_args:
            raise ValueError("Missing required input argument from config: 'genomeSize'")
        if self.threads < 4:
            raise ValueError(
                "Canu requires at least 4 avaliable cores; increase `--threads` to 4 or more"
            )
