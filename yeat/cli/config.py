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
OXFORD = ("canu", "flye")
ALGORITHMS = set(PAIRED + PACBIO + OXFORD)

SHORT_READS = ("paired", "single", "interleaved")
PACBIO_READS = ("pacbio-raw", "pacbio-corr", "pacbio-hifi")
OXFORD_READS = ("nano-raw", "nano-corr", "nano-hq")
LONG_READS = PACBIO_READS + OXFORD_READS
READ_TYPES = SHORT_READS + LONG_READS


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
        self.check_sample_keys()
        for assembler in self.data["assemblers"]:
            self.check_keys(assembler, ("label", "algorithm", "extra_args", "samples"))
        labels = [assembler["label"] for assembler in self.data["assemblers"]]
        if len(labels) > len(set(labels)):
            message = "Duplicate assembly labels: please check config file"
            raise AssemblyConfigurationError(message)

    def check_keys(self, data, keys):
        missingkeys = set(keys) - set(data.keys())
        extrakeys = set(data.keys()) - set(keys)
        if missingkeys:
            keystr = ",".join(sorted(missingkeys))
            message = f"Missing assembly configuration setting(s) '{keystr}'"
            raise AssemblyConfigurationError(message)
        if extrakeys:
            keystr = ",".join(sorted(extrakeys))
            message = f"Ignoring unsupported configuration key(s) '{keystr}'"
            warn(message)

    def check_sample_keys(self):
        for key, value in self.data["samples"].items():
            sample_readtypes = value.keys()
            if len(sample_readtypes) > 1:
                message = f"Multiple read types in sample '{key}'"
                raise AssemblyConfigurationError(message)
            extrakeys = set(sample_readtypes) - set(READ_TYPES)
            if extrakeys:
                keystr = ",".join(sorted(extrakeys))
                message = f"Unsupported read type '{keystr}'"
                raise AssemblyConfigurationError(message)

    def create_sample_and_assembler_objects(self):
        self.samples = {}
        for key, value in self.data["samples"].items():
            self.samples[key] = Sample(value)
        self.assemblers = [
            Assembler(assembler, self.threads) for assembler in self.data["assemblers"]
        ]

    def batch(self):
        self.paired_assemblers = []
        self.pacbio_assemblers = []
        self.oxford_assemblers = []
        for assembler in self.assemblers:
            self.determine_assembler_workflow(assembler)
        self.batch = {
            "paired": {
                "samples": self.get_batch_samples(self.paired_assemblers),
                "assemblers": self.paired_assemblers,
            },
            "pacbio": {
                "samples": self.get_batch_samples(self.pacbio_assemblers),
                "assemblers": self.pacbio_assemblers,
            },
            "oxford": {
                "samples": self.get_batch_samples(self.oxford_assemblers),
                "assemblers": self.oxford_assemblers,
            },
        }

    def determine_assembler_workflow(self, assembler):
        readtypes = set()
        for sample in assembler.samples:
            readtypes.update(set(self.samples[sample].data.keys()))
        if assembler.algorithm in PAIRED and readtypes.intersection(SHORT_READS):
            self.paired_assemblers.append(assembler)
        elif assembler.algorithm in PACBIO and readtypes.intersection(PACBIO_READS):
            self.pacbio_assemblers.append(assembler)
        elif assembler.algorithm in OXFORD and readtypes.intersection(OXFORD_READS):
            self.oxford_assemblers.append(assembler)

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
            samples={key: value.data for key, value in samples.items()},
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
        self.data = data
        self.validate_reads()

    def validate_reads(self):
        for key, value in self.data.items():
            reads = []
            for fastq in value:
                read = Path(fastq).resolve()
                if not read.is_file():
                    raise FileNotFoundError(f"No such file: '{read}'")
                if read in reads:
                    raise AssemblyConfigurationError(f"Found duplicate read sample: '{read}'")
                reads.append(read)


class Assembler:
    def __init__(self, data, threads):
        self.label = data["label"]
        if data["algorithm"] not in ALGORITHMS:
            raise AssemblyConfigurationError(
                f"Unsupported assembly algorithm '{data['algorithm`']}'"
            )
        self.algorithm = data["algorithm"]
        self.samples = data["samples"]
        self.extra_args = data["extra_args"]
        self.threads = threads
        if data["algorithm"] == "canu":
            self.check_canu_required_params()

    def check_canu_required_params(self):
        if "genomeSize=" not in self.extra_args:
            raise ValueError("Missing required input argument from config: 'genomeSize'")
        if self.threads < 4:
            raise ValueError(
                "Canu requires at least 4 avaliable cores; increase `--threads` to 4 or more"
            )
