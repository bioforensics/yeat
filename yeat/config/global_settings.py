# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .downsample_settings import DownsampleGroup
from .filter_settings import FilterGroup
from pydantic import BaseModel, ConfigDict


class GlobalSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    filter: FilterGroup = FilterGroup()
    downsample: DownsampleGroup = DownsampleGroup()

    @classmethod
    def parse_data(cls, data):
        data["filter"] = FilterGroup.parse_data(data.get("filter", {}))
        data["downsample"] = DownsampleGroup.parse_data(data.get("downsample", {}))
        return cls(**data)

    def update_filter_settings(self, data):
        for read_type, filter_data in data.items():
            self.filter.update_settings(read_type, filter_data)

    def update_downsample_settings(self, data):
        for read_type, downsample_data in data.items():
            self.downsample.update_settings(read_type, downsample_data)
