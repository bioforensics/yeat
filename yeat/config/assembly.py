# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import PACBIO_READS, OXFORD_READS, LONG_READS, AssemblyConfigError
from sys import platform


ALGORITHMS = {
    "paired": ("spades", "megahit", "unicycler", "velvet"),
    "single": ("spades", "megahit", "unicycler", "velvet"),
    "pacbio": ("canu", "flye", "hifiasm", "hifiasm_meta", "unicycler", "metamdbg"),
    "oxford": ("canu", "flye", "unicycler"),
    "hybrid": ("unicycler"),
}


class Assembly:
    def __init__(self, label, assembly, threads=1, bandage=False):
        self.label = label
        self.algorithm = assembly["algorithm"]
        self.extra_args = assembly["extra_args"]
        self.samples = assembly["samples"]
        self.mode = assembly["mode"]
        self.low = assembly["low"]
        self.high = assembly["high"]
        self.step = assembly["step"]
        self.threads = threads
        self.bandage = bandage
        self.validate_assembly_configuration()
        self.target_files = self.get_target_files()

    def validate_assembly_configuration(self):
        self.check_valid_mode()
        self.check_valid_algorithm()
        self.check_metaMDBG_OS()
        if self.algorithm == "canu":
            self.check_canu_required_params()
        self.check_sample_readtypes_match_assembly_mode()

    def check_valid_mode(self):
        if self.mode not in ALGORITHMS.keys():
            message = f"Invalid assembly mode '{self.mode}' for '{self.label}'"
            raise AssemblyConfigError(message)

    def check_valid_algorithm(self):
        if self.algorithm not in ALGORITHMS[self.mode]:
            message = f"Invalid assembly algorithm '{self.algorithm}' for '{self.label}'"
            raise AssemblyConfigError(message)

    def check_metaMDBG_OS(self):
        if self.algorithm == "metamdbg" and platform not in ["linux", "linux2"]:
            message = f"Assembly algorithm 'metaMDBG' can only run on 'Linux OS'"
            raise AssemblyConfigError(message)

    def check_canu_required_params(self):
        if "genomeSize=" not in self.extra_args:
            message = f"Missing required extra argument 'genomeSize' for '{self.label}'"
            raise AssemblyConfigError(message)
        if self.threads < 4:
            message = f"Canu requires at least 4 avaliable cores; increase '-t' or '--threads' to 4 or more"
            raise AssemblyConfigError(message)

    def check_sample_readtypes_match_assembly_mode(self):
        for sample in self.samples.values():
            if not self.mode_and_readtypes_are_compatible(sample):
                message = f"No readtypes in '{sample.label}' match '{self.label}' assembly mode '{self.mode}'"
                raise AssemblyConfigError(message)

    def mode_and_readtypes_are_compatible(self, sample):
        if self.mode == "paired":
            return sample.short_readtype == "paired"
        elif self.mode == "single":
            return sample.short_readtype == "single"
        elif self.mode == "pacbio":
            return sample.long_readtype in PACBIO_READS
        elif self.mode == "oxford":
            return sample.long_readtype in OXFORD_READS
        elif self.mode == "hybrid":
            return sample.short_readtype == "paired" and sample.long_readtype in LONG_READS
        else:  # pragma: no cover
            message = f"Invalid assembly mode '{self.mode}'"
            raise AssemblyConfigError(message)

    def get_target_files(self):
        target_files = []
        for sample in self.samples.values():
            target_files.append(self.get_qa_file(sample))
        return target_files

    def get_qa_file(self, sample):
        readtype = self.get_readtype(sample)
        algorithm_dir = f"analysis/{sample.label}/{readtype}/{self.label}/{self.algorithm}"
        if self.bandage:
            return f"{algorithm_dir}/bandage/.done"
        return f"{algorithm_dir}/quast/report.html"

    def get_readtype(self, sample):
        if self.mode in ["paired", "single", "hybrid"]:
            return self.mode
        elif self.mode in ["pacbio", "oxford"]:
            return sample.long_readtype
        else:  # pragma: no cover
            message = f"Invalid assembly mode '{self.mode}'"
            raise AssemblyConfigError(message)
