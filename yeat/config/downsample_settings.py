# -------------------------------------------------------------------------------------------------
# Copyright (c) 2026, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pydantic import BaseModel, ConfigDict, PositiveInt, Field, field_validator
from typing import Literal


class DownsampleSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool = False
    target_depth: PositiveInt = 150
    target_num_reads: PositiveInt | Literal["auto"] = "auto"
    genome_size: PositiveInt | Literal["auto"] = "auto"

    @field_validator("genome_size", mode="before")
    @classmethod
    def parse_genome_size(cls, value):
        if not isinstance(value, str) or value == "auto":
            return value
        value = "".join(value.lower().split())
        multipliers = {
            "k": 1_000,
            "m": 1_000_000,
            "g": 1_000_000_000,
        }
        if value.endswith("b"):
            value = value[:-1]
        suffix = value[-1]
        if suffix in multipliers:
            return int(float(value[:-1]) * multipliers[suffix])
        return value

    @classmethod
    def parse_data(cls, data):
        return cls(**data)

    def update(self, data):
        updated_data = {**self.model_dump(), **data}
        self_type = type(self)
        return self_type(**updated_data)


class ShortDownsampleSettings(DownsampleSettings):
    method: Literal["random", "bbnorm"] = "random"


class LongDownsampleSettings(DownsampleSettings):
    pass


class DownsampleGroup(BaseModel):
    short_downsample_settings: ShortDownsampleSettings = Field(
        default_factory=ShortDownsampleSettings, serialization_alias="short"
    )
    long_downsample_settings: LongDownsampleSettings = Field(
        default_factory=LongDownsampleSettings, serialization_alias="long"
    )

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
