# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from dataclasses import dataclass
import pandas as pd
from pathlib import Path


@dataclass
class Downsample:
    target_num_reads: int
    genome_size: int
    target_depth: int
    average_read_length: int

    @classmethod
    def parse_data(cls, target_num_reads, genome_size, target_depth, mash_report, seqkit_report):
        return cls(
            target_num_reads=target_num_reads,
            genome_size=(
                genome_size if genome_size else cls._get_estimated_genome_size(mash_report)
            ),
            target_depth=target_depth,
            average_read_length=cls._get_average_read_length(seqkit_report),
        )

    @staticmethod
    def _get_estimated_genome_size(mash_report):
        if not Path(mash_report).exists():
            return 0
        df = pd.read_csv(mash_report, sep="\t")
        return int(df.iloc[0]["Length"])

    @staticmethod
    def _get_average_read_length(seqkit_report):
        if not Path(seqkit_report).exists():
            return 0
        df = pd.read_csv(seqkit_report, sep=r"\s+")
        return df.iloc[0]["avg_len"]

    def get_num_reads(self, paired=True):
        if self.target_num_reads:
            return self.target_num_reads
        avl = 2 * self.average_read_length if paired else self.average_read_length
        return int((self.genome_size * self.target_depth) / avl)
