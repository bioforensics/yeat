# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import json
import pandas as pd
from pydantic import BaseModel


class Downsample(BaseModel):
    genome_size: int
    average_read_length: int
    coverage_depth: int
    downsample: int

    @classmethod
    def parse_data(cls, genome_size, mash_report, fastp_report, coverage_depth, downsample):
        return cls(
            genome_size=cls._get_genome_size(genome_size, mash_report),
            average_read_length=cls._get_average_read_length(fastp_report),
            coverage_depth=coverage_depth,
            downsample=downsample,
        )

    @staticmethod
    def _get_genome_size(genome_size, mash_report):
        if genome_size != 0:
            return genome_size
        df = pd.read_csv(mash_report, sep="\t")
        return int(df["Length"].iloc[0])

    @staticmethod
    def _get_average_read_length(fastp_report):
        with open(fastp_report, "r") as fh:
            data = json.load(fh)
        base_count = data["summary"]["after_filtering"]["total_bases"]
        read_count = data["summary"]["after_filtering"]["total_reads"]
        return base_count / read_count

    def get_down(self):
        if self.downsample != 0:
            return self.downsample
        return int((self.genome_size * self.coverage_depth) / (2 * self.average_read_length))
