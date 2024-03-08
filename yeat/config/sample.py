# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import *
from pathlib import Path


class Sample:
    def __init__(self, label, sample):
        self.label = label
        self.sample = sample
        self.all_reads = []
        self.validate_sample_configuration()
        self.short_readtype = self.get_short_readtype()
        self.long_readtype = self.get_long_readtype()
        self.expected_files = self.get_expected_files()

    def validate_sample_configuration(self):
        self.check_enough_readtypes()
        self.check_input_reads()

    def check_enough_readtypes(self):
        if len(self.sample.keys()) == 0:
            message = f"Missing sample reads for '{self.label}'"
            raise AssemblyConfigError(message)
        if len(self.sample.keys()) > 2:
            message = f"Max of 2 readtypes per sample for '{self.label}'"
            raise AssemblyConfigError(message)

    def check_input_reads(self):
        for readtype, reads in self.sample.items():
            if len(reads) == 0:
                message = f"Missing input reads for '{self.label}'"
                raise AssemblyConfigError(message)
            if readtype == "paired":
                for pair in reads:
                    self.check_paired_reads(pair)
                    self.check_reads(pair)
            else:
                self.check_reads(reads)

    def check_paired_reads(self, pair):
        if not isinstance(pair, list):
            message = f"Input read is not a list '{pair}' for '{self.label}'"
            raise AssemblyConfigError(message)
        observed = len(pair)
        expected = 2
        if observed == 0:
            message = f"Missing 2 reads in 'paired' entry for '{self.label}'"
            raise AssemblyConfigError(message)
        if observed < expected:
            message = f"Missing 1 read in 'paired' entry for '{self.label}'"
            raise AssemblyConfigError(message)
        if observed > expected:
            message = f"Found more than 2 reads in 'paired' entry for '{self.label}'"
            raise AssemblyConfigError(message)

    def check_reads(self, reads):
        for read in reads:
            if not isinstance(read, str):
                message = f"Input read is not a string '{read}' for '{self.label}'"
                raise AssemblyConfigError(message)
            if not Path(read).is_file():
                message = f"No such file '{read}' for '{self.label}'"
                raise FileNotFoundError(message)
            if read in self.all_reads:
                message = f"Found duplicate read sample '{read}' for '{self.label}'"
                raise AssemblyConfigError(message)
            self.all_reads.append(read)

    def get_short_readtype(self):
        illumina = set.intersection(set(self.sample.keys()), set(ILLUMINA_READS))
        if len(illumina) > 1:
            message = f"Max of 1 Illumina readtype per sample for '{self.label}'"
            raise AssemblyConfigError(message)
        return next(iter(illumina), None)

    def get_long_readtype(self):
        long = set.intersection(set(self.sample.keys()), set(LONG_READS))
        if len(long) > 1:
            message = f"Max of 1 long readtype per sample for '{self.label}'"
            raise AssemblyConfigError(message)
        return next(iter(long), None)

    def get_expected_files(self):
        expected_files = []
        for readtype in self.sample.keys():
            expected_files += self.get_qc_files(readtype)
        return expected_files

    def get_qc_files(self, readtype):
        if readtype == "paired":
            return [
                f"seq/fastqc/{self.label}/paired/{direction}_combined-reads_fastqc.html"
                for direction in ["r1", "r2"]
            ]
        elif readtype in ("single",) + PACBIO_READS:
            return [f"seq/fastqc/{self.label}/{readtype}/combined-reads_fastqc.html"]
        elif readtype in OXFORD_READS:  # pragma: no cover
            return [
                f"seq/nanoplot/{self.label}/{readtype}/{quality}_LengthvsQualityScatterPlot_dot.pdf"
                for quality in ["raw", "filtered"]
            ]
