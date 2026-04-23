# -------------------------------------------------------------------------------------------------
# Copyright (c) 2026, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pydantic import BaseModel, ConfigDict, PositiveInt
from typing import Literal


class DownsampleSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool = True
    target_depth: PositiveInt = 150
    target_num_reads: PositiveInt | Literal["auto"] = "auto"
    genome_size: PositiveInt | Literal["auto"] = "auto"

    @classmethod
    def parse_data(cls, data):
        return cls(**data)

    def update(self, data):
        extra_keys = set(data.keys()) - set(type(self).model_fields.keys())
        if extra_keys:
            raise DownsampleSettingsError(f"Extra field(s): {', '.join(extra_keys)}")
        return self.model_copy(update=data)


class DownsampleSettingsError(ValueError):
    pass


class ShortDownsampleSettings(DownsampleSettings):
    method: Literal["random", "bbnorm"] = "random"


class LongDownsampleSettings(DownsampleSettings):
    pass


class DownsampleGroup(BaseModel):
    short_downsample_settings: ShortDownsampleSettings = ShortDownsampleSettings()
    long_downsample_settings: LongDownsampleSettings = LongDownsampleSettings()

    @classmethod
    def parse_data(cls, data):
        short_downsample_settings = ShortDownsampleSettings.parse_data(data.get("short", {}))
        long_downsample_settings = LongDownsampleSettings.parse_data(data.get("long", {}))
        return cls(
            short_downsample_settings=short_downsample_settings,
            long_downsample_settings=long_downsample_settings,
        )

    def update_settings(self, read_type, data):
        if read_type == "short":
            self.short_downsample_settings = self.short_downsample_settings.update(data)
        else:
            self.long_downsample_settings = self.long_downsample_settings.update(data)
