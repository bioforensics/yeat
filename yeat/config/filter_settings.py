# -------------------------------------------------------------------------------------------------
# Copyright (c) 2026, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pydantic import BaseModel, ConfigDict, Field


class FilterSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool = False

    @classmethod
    def parse_data(cls, data):
        return cls(**data)

    def update(self, data):
        updated_data = {**self.model_dump(), **data}
        self_type = type(self)
        return self_type(**updated_data)


class ShortFilterSettings(FilterSettings):
    fastp_args: str = "--min-length 50 --detect_adapter_for_pe"


class LongFilterSettings(FilterSettings):
    chopper_args: str = ""


class FilterGroup(BaseModel):
    short_filter_settings: ShortFilterSettings = Field(
        default_factory=ShortFilterSettings, serialization_alias="short"
    )
    long_filter_settings: LongFilterSettings = Field(
        default_factory=LongFilterSettings, serialization_alias="long"
    )

    @classmethod
    def parse_data(cls, data):
        short_filter_settings = ShortFilterSettings.parse_data(data.get("short", {}))
        long_filter_settings = LongFilterSettings.parse_data(data.get("long", {}))
        return cls(
            short_filter_settings=short_filter_settings, long_filter_settings=long_filter_settings
        )

    def update_settings(self, read_type, data):
        if read_type == "short":
            self.short_filter_settings = self.short_filter_settings.update(data)
        else:
            self.long_filter_settings = self.long_filter_settings.update(data)
