# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union, List


@dataclass
class Sample:
    illumina: Optional[Union[List[str], str]] = None
    ont: Optional[str] = None
    ont_ultra_long: Optional[str] = None  # update everything here <-------------------
    pacbio: Optional[str] = None
    downsample: Optional[
        int
    ] = -1  # update these variables here based on CLI!!! if cli is filled out, override toml
    genome_size: Optional[int] = -1
    coverage_depth: Optional[int] = -1
    hybrid: bool = False

    def __post_init__(self):
        self.check_input_data()
        self.check_file_paths()
        self.check_hybrid_sample()

    def __str__(self):
        if self.illumina:
            return f"illumina: {self.illumina}"
        if self.ont:
            return f"ont: {self.ont}"
        if self.pacbio:
            return f"pacbio: {self.pacbio}"

    def check_input_data(self):
        if not self.illumina and not self.ont and not self.pacbio:
            raise "Sample does not have any reads"
        if self.ont and self.pacbio:
            raise "Too many long read types"
        if self.illumina:
            if isinstance(self.illumina, list):
                if len(self.illumina) < 2:
                    raise "Missing paired reads"
                elif len(self.illumina) > 2:
                    raise "Too many paired reads"

    def check_file_paths(self):
        message = "File does not exist"
        if self.illumina:
            if isinstance(self.illumina, list):
                for read in self.illumina:
                    if not Path(read).exists():
                        raise message
            else:
                if not Path(self.illumina).exists():
                    raise message
        if self.ont:
            if not Path(self.ont).exists():
                raise message
        if self.pacbio:
            if not Path(self.pacbio).exists():
                raise message

    def check_hybrid_sample(self):
        if self.illumina and (self.ont or self.pacbio):
            if len(self.illumina) == 2:
                self.hybrid = True
            else:
                raise "Sample does not have correct hybrid reads"

    def get_target_files(self):
        target_files = []
        if self.hybrid:
            target_files.append("qc/illumina/downsample/R1.fastq.gz")
            target_files.append("qc/illumina/downsample/R2.fastq.gz")
            target_files.append("qc/illumina/fastqc/R1_fastqc.html")
            target_files.append("qc/illumina/fastqc/R2_fastqc.html")
            if self.ont:
                target_files.append("qc/ont/downsample/read.fastq.gz")
            elif self.pacbio:
                target_files.append("qc/pacbio/downsample/read.fastq.gz")
            return target_files
        if self.illumina:
            if isinstance(self.illumina, list):
                target_files.append("qc/illumina/downsample/R1.fastq.gz")
                target_files.append("qc/illumina/downsample/R2.fastq.gz")
                target_files.append("qc/illumina/fastqc/R1_fastqc.html")
                target_files.append("qc/illumina/fastqc/R2_fastqc.html")
            else:
                target_files.append("qc/illumina/downsample/read.fastq.gz")
                target_files.append("qc/illumina/fastqc/read_fastqc.html")
            return target_files
        if self.ont:
            target_files.append("qc/ont/downsample/read.fastq.gz")
            target_files.append("qc/ont/fastqc/read_fastqc.html")
            return target_files
        if self.pacbio:
            target_files.append("qc/pacbio/downsample/read.fastq.gz")
            target_files.append("qc/pacbio/fastqc/read_fastqc.html")
            return target_files

    # def get_sample_type(self):
    #     if self.hybrid:
    #         return "hybrid"
    #     elif self.illumina:
    #         return "illumina"
    #     elif self.ont:
    #         return "ont"
    #     elif self.pacbio:
    #         return "pacbio"


#     def check_input_downsample_values(self):
#         if self.sample["downsample"] < -1:
#             message = f"Invalid input '{self.sample['downsample']}' for '{self.label}'"
#             raise AssemblyConfigError(message)
#         if self.sample["genome_size"] < 0:
#             message = f"Invalid input '{self.sample['genome_size']}' for '{self.label}'"
#             raise AssemblyConfigError(message)
#         if self.sample["coverage_depth"] < 1:
#             message = f"Invalid input '{self.sample['coverage_depth']}' for '{self.label}'"
#             raise AssemblyConfigError(message)


#     def get_target_files(self):
#         target_files = []
#         for readtype in self.sample.keys():
#             if readtype not in READ_TYPES:
#                 continue
#             target_files += self.get_qc_files(readtype)
#         return target_files


#     def get_qc_files(self, readtype):
#         if readtype == "paired":
#             return [
#                 f"{self.label}/yeat/qc/{direction}_combined-reads_fastqc.html"
#                 for direction in ["r1", "r2"]
#             ]
#         elif readtype in ("single",) + PACBIO_READS:
#             return [f"seq/fastqc/{self.label}/{readtype}/combined-reads_fastqc.html"]
#         elif readtype in OXFORD_READS:
#             return [
#                 f"seq/nanoplot/{self.label}/{readtype}/{quality}_LengthvsQualityScatterPlot_dot.pdf"
#                 for quality in ["raw", "filtered"]
#             ]
#         else:  # pragma: no cover
#             message = f"Invalid readtype '{readtype}'"
#             raise AssemblyConfigError(message)
