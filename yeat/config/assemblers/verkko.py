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


class VerkkoAssembler(Assembler):
    @staticmethod
    def _check_sample_compatibility(sample):
        return sample.has_long_reads

    @property
    def targets(self):
        targets = list()
        for sample in self.samples.values():
            label_dir = f"analysis/{sample.label}/yeat/verkko/{self.label}"
            targets.append(f"{label_dir}/quast/report.html")
            targets.append(f"{label_dir}/bandage/.done")
        return targets

    def input_files(self, sample):
        infiles = dict()
        if "pacbio_hifi" in self.samples[sample].data:
            infiles["pacbio_hifi"] = f"analysis/{sample}/qc/pacbio_hifi/downsample/read.fastq.gz"
        if "ont_duplex" in self.samples[sample].data:
            infiles["ont_duplex"] = f"analysis/{sample}/qc/ont_duplex/downsample/read.fastq.gz"
        if "ont_ultralong" in self.samples[sample].data:
            infiles["ont_ultralong"] = (
                f"analysis/{sample}/qc/ont_ultralong/downsample/read.fastq.gz"
            )
        return infiles

    def input_args(self, sample):
        reads = self.input_files(sample)
        print(reads)
        assert 0
        # if len(reads) == 1 and self.samples[sample].has_illumina:
        #     args = f"-s {reads[0]}"
        # elif len(reads) == 2 and self.samples[sample].has_illumina:
        #     args = f"-1 {reads[0]} -2 {reads[1]}"
        # elif len(reads) == 1 and self.samples[sample].has_long_reads:
        #     args = f"-l {reads[0]}"
        # elif len(reads) == 3:
        #     args = f"-1 {reads[0]} -2 {reads[1]} -l {reads[2]}"
        # else:
        #     assert 0  # pragma: no cover
        # return args

    def gfa_files(self, sample):
        return glob(f"analysis/{sample}/yeat/verkko/{self.label}/*.gfa")
