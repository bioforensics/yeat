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


class SPAdesAssembler(Assembler):
    @staticmethod
    def _check_sample_compatibility(sample):
        return sample.has_illumina

    @property
    def targets(self):
        targets = list()
        for sample in self.samples.values():
            label_dir = f"analysis/{sample.label}/yeat/spades/{self.label}"
            targets.append(f"{label_dir}/quast/report.html")
            targets.append(f"{label_dir}/bandage/.done")
        return targets

    def input_files(self, sample):
        infiles = {}
        sample_path = f"analysis/{sample}/qc"
        sample_obj = self.samples[sample]
        infiles.update(self.get_illumina_files(sample_path, sample_obj))
        infiles.update(self.get_long_file(sample_path, sample_obj))
        return infiles

    def get_illumina_files(self, sample_path, sample_obj):
        reads = sample_obj.data["illumina"]
        downsample_dir = f"{sample_path}/illumina/downsample"
        if len(reads) == 1:
            return {"illumina": [f"{downsample_dir}/read.fastq.gz"]}
        return {"illumina": [f"{downsample_dir}/R1.fastq.gz", f"{downsample_dir}/R2.fastq.gz"]}

    def get_long_file(self, sample_path, sample_obj):
        long_read_type = sample_obj.best_long_read_type
        if long_read_type:
            return {long_read_type: [f"{sample_path}/{long_read_type}/downsample/read.fastq.gz"]}
        return {}

    def input_args(self, sample):
        reads = self.input_files(sample)
        args = []
        args.extend(self.get_illumina_args(reads))
        args.extend(self.get_long_args(sample, reads))
        return " ".join(args)

    def get_illumina_args(self, reads):
        illumina_reads = reads["illumina"]
        if len(illumina_reads) == 1:
            return ["-s", illumina_reads[0]]
        return ["-1", illumina_reads[0], "-2", illumina_reads[1]]

    def get_long_args(self, sample, reads):
        long_read_type = self.samples[sample].best_long_read_type
        if long_read_type:
            long_reads = reads.get(long_read_type)
            if long_read_type == "pacbio_hifi":
                return ["--pacbio", long_reads[0]]
            elif long_read_type.startswith("ont_"):
                return ["--nanopore", long_reads[0]]
        return []

    def gfa_files(self, sample):
        label_dir = f"analysis/{sample}/yeat/spades/{self.label}"
        return glob(f"{label_dir}/*.gfa") + glob(f"{label_dir}/*.fastg")
