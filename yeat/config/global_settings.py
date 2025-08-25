# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pydantic import BaseModel, ConfigDict
from typing import Optional


class GlobalSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_coverage_depth: Optional[int] = 150
    target_num_reads: Optional[int] = -1  # -1 disable, 0 auto
    genome_size: Optional[int] = 0  # 0 auto
    min_length: Optional[int] = 100
    quality: Optional[int] = 10
    skip_filter: Optional[bool] = False

    @classmethod
    def parse_data(cls, data):
        return cls(**data)