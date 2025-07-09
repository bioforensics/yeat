# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .assembler import Assembler


class SPAdesAssembler(Assembler):
    def hello(self):
        pass

    #     @property
    #     def compatible_samples(self):
    #         return sorted(label for label, sample in self.samples.items() if sample.has_illumina)

    # def input_args(self, sample):
    #     if sample not in self.compatible_samples:
    #         raise KeyError(f"sample {sample} not found")
    #     reads = self.samples[sample].fastp_targets
    #     if len(reads) not in (1, 2):
    #         raise ValueError(f"expected 1 or 2 FASTQ files, not {len(reads)}")
    #     if len(reads) == 1:
    #         args = f"-s {reads[0]}"
    #     else:
    #         args = f"-1 {reads[0]} -2 {reads[1]}"
    #     return args

    def contig_file(self, sample):
        return f"analysis/{sample}/yeat/{self.label}/spades/contigs.fasta"

    def graph_file(self, sample):
        return f"analysis/{sample}/yeat/{self.label}/spades/graph_files.txt"

    def quast_file(self, sample):
        return f"analysis/{sample}/yeat/spades/{self.label}/quast/report.html"

    def quast_files(self):
        temp = []
        for sample in self.samples.values():
            temp.append(f"analysis/{sample.label}/yeat/spades/{self.label}/quast/report.html")
        return temp


class SampleConfigurationError(ValueError):
    pass
