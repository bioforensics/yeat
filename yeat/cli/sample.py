# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .aux import AssemblyConfigError
from collections import defaultdict
from pathlib import Path


class Sample:
    def __init__(self, label, data):
        self.label = label
        self.reads = self.get_reads(data)
        self.validate()

    def get_reads(self, data):
        reads = defaultdict(list)
        for key, value in data.items():
            if not value:
                message = f"Missing '{key}' entries for '{self.label}'"
                raise AssemblyConfigError(message)
            if key == "paired":
                for read in value:
                    self.check_paired_entry(read)
                    reads[key].append([Path(fastq).resolve() for fastq in read])
                continue
            for fastq in value:
                reads[key].append(Path(fastq).resolve())
        return reads

    def check_paired_entry(self, read):
        observed = len(read)
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

    def validate(self):
        reads = []
        for key, value in self.reads.items():
            if key == "paired":
                for read in value:
                    for fastq in read:
                        self.check_fastq(fastq, reads)
                        reads.append(fastq)
                continue
            for fastq in value:
                self.check_fastq(fastq, reads)
                reads.append(fastq)

    def check_fastq(self, fastq, reads):
        if not fastq.is_file():
            message = f"No such file '{fastq}' for '{self.label}'"
            raise FileNotFoundError(message)
        if fastq in reads:
            message = f"Found duplicate read sample '{fastq}' for '{self.label}'"
            raise AssemblyConfigError(message)

    # def get_specific_reads(self, readtype):
    #     if

    def to_string(self):
        print(self.reads)
        assert 0
        return self.reads
