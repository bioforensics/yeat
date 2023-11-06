# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .aux import AssemblyConfigError
from sys import platform


PAIRED = ("spades", "megahit", "unicycler")
SINGLE = ("spades", "megahit", "unicycler")
PACBIO = ("canu", "flye", "hifiasm", "hifiasm-meta", "unicycler", "metamdbg")
OXFORD = ("canu", "flye", "unicycler")
HYBRID = ("unicycler",)
ILLUMINA_ALGORITHMS = set(PAIRED + SINGLE)
LONG_ALGORITHMS = set(PACBIO + OXFORD)
HYBRID_ALGORITHMS = set(HYBRID)
ALGORITHMS = set.union(*[ILLUMINA_ALGORITHMS, LONG_ALGORITHMS, HYBRID_ALGORITHMS])

MODES = ("paired", "single", "pacbio", "nanopore", "hybrid")


class Assembly:
    def __init__(self, label, data, threads):
        self.label = label
        self.algorithm = data["algorithm"]
        self.extra_args = data["extra_args"]
        self.samples = data["samples"]
        self.mode = data["mode"]
        self.threads = threads
        self.validate()

    def validate(self):
        self.check_valid_algorithm()
        self.check_valid_mode()
        if self.algorithm == "canu":
            self.check_canu_required_params()

    def check_valid_algorithm(self):
        if self.algorithm not in ALGORITHMS:
            message = f"Unsupported assembly algorithm '{self.algorithm}' for '{self.label}'"
            raise AssemblyConfigError(message)
        if self.algorithm == "metamdbg" and platform not in ["linux", "linux2"]:
            message = f"Assembly algorithm 'metaMDBG' can only run on 'Linux OS'"
            raise AssemblyConfigError(message)

    def check_valid_mode(self):
        if self.mode not in MODES:
            message = f"Invalid mode '{self.mode}' for '{self.label}'"
            raise AssemblyConfigError(message)
        if (
            (self.mode == "paired" and self.algorithm not in PAIRED)
            or (self.mode == "single" and self.algorithm not in SINGLE)
            or (self.mode == "pacbio" and self.algorithm not in PACBIO)
            or (self.mode == "nanopore" and self.algorithm not in OXFORD)
            or (self.mode == "hybrid" and self.algorithm not in HYBRID)
        ):
            message = f"Incompatible mode '{self.mode}' with assembly algorithm '{self.algorithm}' for '{self.label}"
            raise AssemblyConfigError(message)

    def check_canu_required_params(self):
        if "genomeSize=" not in self.extra_args:
            message = (
                f"Missing required input argument from config 'genomeSize' for '{self.label}'"
            )
            raise AssemblyConfigError(message)
        if self.threads < 4:
            message = f"Canu requires at least 4 avaliable cores; increase `--threads` to 4 or more for '{self.label}'"
            raise AssemblyConfigError(message)
