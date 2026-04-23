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
from typing import Literal


@dataclass
class Downsample:
    target_depth: int
    target_num_reads: int
    genome_size: int
    average_read_length: int
    read_type: Literal["paired", "single", "long"]

    def __post_init__(self):
        if self.target_num_reads:
            return
        avl = (
            2 * self.average_read_length
            if self.read_type == "paired"
            else self.average_read_length
        )
        self.target_num_reads = int((self.genome_size * self.target_depth) / avl)

    @classmethod
    def parse_data(
        cls, target_depth, target_num_reads, genome_size, mash_report, seqkit_report, read_type
    ):
        return cls(
            target_depth=target_depth,
            target_num_reads=target_num_reads if isinstance(target_num_reads, int) else None,
            genome_size=(
                genome_size
                if isinstance(genome_size, int)
                else cls._get_estimated_genome_size(mash_report)
            ),
            average_read_length=cls._get_average_read_length(seqkit_report),
            read_type=read_type,
        )

    @staticmethod
    def _get_estimated_genome_size(mash_report):
        df = pd.read_csv(mash_report, sep="\t")
        return int(df.iloc[0]["Length"])

    @staticmethod
    def _get_average_read_length(seqkit_report):
        df = pd.read_csv(seqkit_report, sep=r"\s+")
        return int(float(df.iloc[0]["avg_len"].replace(",", "")))
