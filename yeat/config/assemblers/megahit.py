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
            targets.append(f"analysis/{sample.label}/yeat/megahit/{self.label}/quast/report.html")
            targets.append(f"analysis/{sample.label}/yeat/megahit/{self.label}/bandage/.done")
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
            args = f"-r {reads[0]}"
        else:
            args = f"-1 {reads[0]} -2 {reads[1]}"
        return args

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

    def get_and_filter_contig_files(self, sample):
        pattern = (
            rf"analysis/{sample}/yeat/megahit/{self.label}/intermediate_contigs/k\d+.contigs.fa"
        )
        contigs = glob(
            f"analysis/{sample}/yeat/megahit/{self.label}/intermediate_contigs/k*.contigs.fa"
        )
        return filter(re.compile(pattern).match, contigs)
