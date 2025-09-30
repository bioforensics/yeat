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
    def targets(self):
        targets = list()
        for sample in self.samples.values():
            targets.append(f"analysis/{sample.label}/yeat/penguin/{self.label}/quast/report.html")
        return targets

    def input_files(self, sample):
        sample_path = f"analysis/{sample}/qc"
        sample_obj = self.samples[sample]
        reads = sample_obj.data["illumina"]
        downsample_dir = f"{sample_path}/illumina/downsample"
        if len(reads) == 1:
            return {"illumina": [f"{downsample_dir}/read.fastq.gz"]}
        return {"illumina": [f"{downsample_dir}/R1.fastq.gz", f"{downsample_dir}/R2.fastq.gz"]}

    def input_args(self, sample):
        reads = self.input_files(sample)
        args = list()
        args.extend(self.get_illumina_args(reads))
        return " ".join(args)

    def get_illumina_args(self, reads):
        illumina_reads = reads["illumina"]
        if len(illumina_reads) == 1:
            return [illumina_reads[0]]
        return [illumina_reads[0], illumina_reads[1]]

    def bowtie2_input_args(self, sample):
        reads = self.input_files(sample)
        illumina_reads = reads["illumina"]
        if len(illumina_reads) == 1:
            return f"-U {illumina_reads[0]}"
        return f"-1 {illumina_reads[0]} -2 {illumina_reads[1]}"
