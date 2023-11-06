# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .assembly import Assembly
from .aux import AssemblyConfigError
from .sample import Sample
from collections import defaultdict
import json


ILLUMINA_READS = ("paired", "single")
PACBIO_READS = ("pacbio-raw", "pacbio-corr", "pacbio-hifi")
OXFORD_READS = ("nano-raw", "nano-corr", "nano-hq")
LONG_READS = PACBIO_READS + OXFORD_READS
READ_TYPES = ILLUMINA_READS + LONG_READS

BASE_KEYS = ("samples", "assemblies")
ASSEMBLY_KEYS = ("algorithm", "extra_args", "samples", "mode")


class AssemblyConfig:
    def __init__(self, data, threads):
        self.data = data
        self.validate()
        self.threads = threads
        self.create_sample_and_assembly_objects()
        self.sort()
        self.batch()

    @classmethod
    def from_json(cls, infile, threads):
        data = json.load(open(infile))
        return cls(data, threads)

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

    def sort(self):
        self.paired_sample_labels = set()
        self.paired_assemblies = []
        self.single_sample_labels = set()
        self.single_assemblies = []
        self.pacbio_sample_labels = set()
        self.pacbio_assemblies = []
        self.oxford_sample_labels = set()
        self.oxford_assemblies = []
        self.hybrid_sample_labels = set()
        self.hybrid_assemblies = []
        for key, value in self.assemblies.items():
            if value.mode == "paired":
                self.paired_sample_labels.update(value.samples)
                self.paired_assemblies.append(value)
            elif value.mode == "single":
                self.single_sample_labels.update(value.samples)
                self.single_assemblies.append(value)
            elif value.mode == "pacbio":
                self.pacbio_sample_labels.update(value.samples)
                self.pacbio_assemblies.append(value)
            elif value.mode == "oxford":
                self.oxford_sample_labels.update(value.samples)
                self.oxford_assemblies.append(value)
            elif value.mode == "hybrid":
                self.hybrid_sample_labels.update(value.samples)
                self.hybrid_assemblies.append(value)

    def batch(self):
        self.batch = {
            "paired": {
                "samples": self.get_samples(self.paired_sample_labels, "paired"),
                "assemblies": self.paired_assemblies,
            },
            "single": {
                "samples": self.get_samples(self.single_sample_labels, "single"),
                "assemblies": self.single_assemblies,
            },
            "pacbio": {
                "samples": self.get_samples(self.pacbio_sample_labels, "pacbio"),
                "assemblies": self.pacbio_assemblies,
            },
            "oxford": {
                "samples": self.get_samples(self.oxford_sample_labels, "oxford"),
                "assemblies": self.oxford_assemblies,
            },
            "hybrid": {
                "samples": self.get_samples(self.hybrid_sample_labels, "hybrid"),
                "assemblies": self.hybrid_assemblies,
            },
        }

    def get_samples(self, labels, mode):
        temp = {}
        for label in labels:
            reads = self.samples[label].reads
            for key, value in reads.items():
                string = defaultdict(list)
                if key == "paired":
                    for v in value:
                        string[key].append([str(x) for x in v])
                else:
                    for v in value:
                        string[key].append(str(v))
                if mode in key:
                    temp[label] = dict(string)
        return temp

    def to_dict(self, args, readtype):
        samples = self.batch[readtype]["samples"]
        assemblies = self.batch[readtype]["assemblies"]
        label_to_samples = {}
        for assembly in assemblies:
            label_to_samples[assembly.label] = [
                sample for sample in assembly.samples if sample in samples
            ]
        temp = dict(
            samples=list(samples.keys()),
            reads=samples,
            labels=[assembly.label for assembly in assemblies],
            assemblies={assembly.label: assembly.algorithm for assembly in assemblies},
            extra_args={assembly.label: assembly.extra_args for assembly in assemblies},
            label_to_samples=label_to_samples,
            sample_readtype={label: list(sample.keys()) for label, sample in samples.items()},
            threads=args.threads,
            downsample=args.downsample,
            coverage=args.coverage,
            genomesize=args.genome_size,
            seed=args.seed,
            length_required=args.length_required,
        )
        return temp
