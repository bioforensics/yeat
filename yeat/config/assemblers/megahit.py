# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .assembler import Assembler
from pathlib import Path
import re
import subprocess


class MEGAHITAssembler(Assembler):
    @staticmethod
    def _check_sample_compatibility(sample):
        return sample.has_illumina

    @property
    def targets(self):
        targets = list()
        for sample in self.samples.values():
            label_dir = f"analysis/{sample.label}/yeat/megahit/{self.label}"
            targets.append(f"{label_dir}/quast/report.html")
            targets.append(f"{label_dir}/bandage/.done")
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
            return ["-r", illumina_reads[0]]
        return ["-1", illumina_reads[0], "-2", illumina_reads[1]]

    def gfa_files(self, sample):
        gfa_files = []
        intermediates_dir = Path(
            f"analysis/{sample}/yeat/megahit/{self.label}/intermediate_contigs"
        )
        fa_files = intermediates_dir.glob("k*.contigs.fa")
        for fa in fa_files:
            match = re.match(r"k(\d+)\.contigs\.fa", fa.name)
            if not match:
                continue
            kmer = match.group(1)
            fastg = intermediates_dir / f"{fa.stem}.fastg"
            with open(fastg, "w") as out_file:
                subprocess.run(
                    ["megahit_toolkit", "contig2fastg", kmer, str(fa)],
                    stdout=out_file,
                    stderr=subprocess.PIPE,
                    check=True,
                )
            gfa_files.append(str(fastg))
        return gfa_files
