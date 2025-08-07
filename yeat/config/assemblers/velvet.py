# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .assembler import Assembler
from glob import glob


class VelvetAssembler(Assembler):
    @staticmethod
    def _check_sample_compatibility(sample):
        return sample.has_illumina

    @property
    def targets(self):
        targets = list()
        for sample in self.samples.values():
            label_dir = f"analysis/{sample.label}/yeat/velvet/{self.label}"
            targets.append(f"{label_dir}/quast/report.html")
            targets.append(f"{label_dir}/bandage/.done")
        return targets

    def input_files(self, sample):
        reads = self.samples[sample].data["illumina"]
        downsample_dir = f"analysis/{sample}/qc/illumina/downsample"
        if len(reads) == 1:
            return [f"{downsample_dir}/read.fastq.gz"]
        r1 = f"{downsample_dir}/R1.fastq.gz"
        r2 = f"{downsample_dir}/R2.fastq.gz"
        return [r1, r2]

    def input_args(self, sample):
        reads = self.input_files(sample)
        if len(reads) == 1:
            return f"'-fastq.gz {reads[0]}'"
        return f"'-fastq.gz -shortPaired {reads[0]} -shortPaired2 {reads[1]}'"

    def gfa_files(self, sample):
        return glob(f"analysis/{sample}/yeat/velvet/{self.label}/Graph*")
