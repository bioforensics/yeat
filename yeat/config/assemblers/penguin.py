# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .assembler import Assembler


class PenguiNAssembler(Assembler):
    @staticmethod
    def _check_sample_compatibility(sample):
        return sample.has_illumina

    @property
    def target_files(self):
        targets = list()
        for sample in self.samples.values():
            targets.append(f"analysis/{sample.label}/yeat/penguin/{self.label}/quast/report.html")
        return targets

    def input_files(self, sample):
        reads = self.samples[sample].data["illumina"]
        if len(reads) == 1:
            return [f"analysis/{sample}/qc/illumina/downsample/read.fastq.gz"]
        r1 = f"analysis/{sample}/qc/illumina/downsample/R1.fastq.gz"
        r2 = f"analysis/{sample}/qc/illumina/downsample/R2.fastq.gz"
        return [r1, r2]

    def input_args(self, sample):
        reads = self.input_files(sample)
        if len(reads) == 1:
            args = f"{reads[0]}"
        else:
            args = f"{reads[0]} {reads[1]}"
        return args

    def bowtie2_input_args(self, sample):
        reads = self.input_files(sample)
        if len(reads) == 1:
            args = f"-U {reads[0]}"
        else:
            args = f"-1 {reads[0]} -2 {reads[1]}"
        return args
