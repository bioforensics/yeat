# -------------------------------------------------------------------------------------------------
# Copyright (c) 2026, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pydantic import BaseModel, ConfigDict


class FilterSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool = True

    @classmethod
    def parse_data(cls, data):
        return cls(**data)

    def update(self, data):
        extra_keys = set(data.keys()) - set(type(self).model_fields.keys())
        if extra_keys:
            raise FilterSettingsError(f"Extra field(s): {', '.join(extra_keys)}")
        return self.model_copy(update=data)


class FilterSettingsError(ValueError):
    pass


class ShortFilterSettings(FilterSettings):
    fastp_args: str = ""


class LongFilterSettings(FilterSettings):
    chopper_args: str = ""


class FilterGroup(BaseModel):
    short_filter_settings: ShortFilterSettings
    long_filter_settings: LongFilterSettings

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
