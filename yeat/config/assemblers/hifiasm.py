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


class HifiasmAssembler(Assembler):
    @staticmethod
    def _check_sample_compatibility(sample):
        return sample.has_long_reads

    @property
    def targets(self):
        targets = list()
        for sample in self.samples.values():
            label_dir = f"analysis/{sample.label}/yeat/hifiasm/{self.label}"
            targets.append(f"{label_dir}/quast/report.html")
            targets.append(f"{label_dir}/bandage/.done")
        return targets

    def input_files(self, sample):
        infiles = dict()
        best_read_type = self.samples[sample].best_long_read_type
        infiles[best_read_type] = [
            f"analysis/{sample}/qc/{best_read_type}/downsample/read.fastq.gz"
        ]
        return infiles

    def input_args(self, sample):
        reads = self.input_files(sample)
        args = list()
        args.extend(self.get_long_args(sample, reads))
        return " ".join(args)

    def get_long_args(self, sample, reads):
        long_read_type = self.samples[sample].best_long_read_type
        long_reads = reads.get(long_read_type)
        if long_read_type in ["ont_simplex", "ont_duplex"]:
            return ["--ont", long_reads[0]]
        if long_read_type in ["ont_ultralong"]:
            return ["--ul", long_reads[0]]
        return ["-pacbio-hifi", long_reads[0]]

    def gfa_files(self, sample):
        return glob(f"analysis/{sample}/yeat/hifiasm/{self.label}/*.gfa")
