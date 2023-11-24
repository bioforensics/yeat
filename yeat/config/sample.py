# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import ILLUMINA_READS, LONG_READS, AssemblyConfigError
from pathlib import Path


class Sample:
    def __init__(self, label, data):
        self.label = label
        self.data = data
        self.validate()

    def validate(self):
        self.check_one_readtype_limit()
        self.check_input_reads()

    def check_one_readtype_limit(self):
        observed_readtypes = self.data.keys()
        if len(observed_readtypes) == 0:
            message = f"Missing sample reads for '{self.label}'"
            raise AssemblyConfigError(message)
        if len(observed_readtypes) > 2:
            message = f"Max of 2 readtypes per sample for '{self.label}'"
            raise AssemblyConfigError(message)
        illumina = set.intersection(set(observed_readtypes), set(ILLUMINA_READS))
        if len(illumina) > 1:
            message = f"Max of 1 Illumina readtype per sample for '{self.label}'"
            raise AssemblyConfigError(message)
        long = set.intersection(set(observed_readtypes), set(LONG_READS))
        if len(long) > 1:
            message = f"Max of 1 long readtype per sample for '{self.label}'"
            raise AssemblyConfigError(message)
        self.short_readtype = next(iter(illumina)) if illumina else None
        self.long_readtype = next(iter(long)) if long else None

    def check_input_reads(self):
        self.all_reads = []
        for readtype, reads in self.data.items():
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
