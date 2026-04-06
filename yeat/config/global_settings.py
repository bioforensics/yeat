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


class FilterSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: Optional[bool] = True
    min_length: Optional[int] = 100
    quality: Optional[int] = 15

    @classmethod
    def parse_data(cls, data):
        return cls(**data)

    def update(self, data):
        invalid_keys = set(data.keys()) - set(self.model_fields.keys())
        if invalid_keys:
            raise ValueError(f"Invalid field(s): {', '.join(invalid_keys)}")
        return self.model_copy(update=data)


class DownsampleSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    method: Optional[str] = "none"
    target_num_reads: Optional[int] = 0
    genome_size: Optional[int] = 0
    target_depth: Optional[int] = 150

    @classmethod
    def parse_data(cls, data):
        return cls(**data)

    def update(self, data):
        invalid_keys = set(data.keys()) - set(self.model_fields.keys())
        if invalid_keys:
            raise ValueError(f"Invalid field(s): {', '.join(invalid_keys)}")
        return self.model_copy(update=data)


class GlobalSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    filter: FilterSettings
    downsample: DownsampleSettings

    @classmethod
    def parse_data(cls, data):
        data["filter"] = FilterSettings.parse_data(data.get("filter", {}))
        data["downsample"] = DownsampleSettings.parse_data(data.get("downsample", {}))
        return cls(**data)
