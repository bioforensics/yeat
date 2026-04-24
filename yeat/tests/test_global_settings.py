# -------------------------------------------------------------------------------------------------
# Copyright (c) 2026, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pydantic import ValidationError
import pytest
from yeat.config.global_settings import (
    FilterSettings,
    FilterSettingsError,
    DownsampleSettings,
    DownsampleSettingsError,
    GlobalSettings,
)


@pytest.mark.parametrize(
    "data,expected",
    [
        (
            {"enabled": True, "min_length": 250, "quality": 10},
            {"enabled": True, "min_length": 250, "quality": 10},
        ),
        ({"enabled": False}, {"enabled": False, "min_length": 100, "quality": 15}),
        ({}, {"enabled": True, "min_length": 100, "quality": 15}),
    ],
)
def test_filter_settings_parse_data(data, expected):
    filter_settings = FilterSettings.parse_data(data)
    assert filter_settings.model_dump() == expected


def test_filter_settings_parse_data_extra_keys():
    message = r"Extra inputs are not permitted \[type=extra_forbidden, input_value='INVALID'"
    with pytest.raises(ValidationError, match=message):
        FilterSettings.parse_data({"INVALID": "INVALID"})


@pytest.mark.parametrize(
    "data,expected",
    [
        (
            {"enabled": True, "min_length": 250, "quality": 10},
            {"enabled": True, "min_length": 250, "quality": 10},
        ),
        ({"enabled": False}, {"enabled": False, "min_length": 100, "quality": 15}),
        ({}, {"enabled": True, "min_length": 100, "quality": 15}),
    ],
)
def test_filter_settings_update(data, expected):
    filter_settings = FilterSettings()
    filter_settings = filter_settings.update(data)
    assert filter_settings.model_dump() == expected


def test_filter_settings_update_extra_keys():
    message = r"Extra field\(s\): INVALID"
    with pytest.raises(FilterSettingsError, match=message):
        filter_settings = FilterSettings()
        filter_settings = filter_settings.update({"INVALID": "INVALID"})


@pytest.mark.parametrize(
    "data,expected",
    [
        (
            {
                "method": "random",
                "target_num_reads": 0,
                "genome_size": 4600000,
                "target_depth": 250,
            },
            {
                "method": "random",
                "target_num_reads": 0,
                "genome_size": 4600000,
                "target_depth": 250,
            },
        ),
        (
            {"method": "random"},
            {"method": "random", "target_num_reads": 0, "genome_size": 0, "target_depth": 150},
        ),
        ({}, {"method": "none", "target_num_reads": 0, "genome_size": 0, "target_depth": 150}),
    ],
)
def test_downsample_settings_parse_data(data, expected):
    downsample_settings = DownsampleSettings.parse_data(data)
    assert downsample_settings.model_dump() == expected


def test_downsample_settings_parse_data_extra_keys():
    message = r"Extra inputs are not permitted \[type=extra_forbidden, input_value='INVALID'"
    with pytest.raises(ValidationError, match=message):
        DownsampleSettings.parse_data({"INVALID": "INVALID"})


@pytest.mark.parametrize(
    "data,expected",
    [
        (
            {
                "method": "random",
                "target_num_reads": 0,
                "genome_size": 4600000,
                "target_depth": 250,
            },
            {
                "method": "random",
                "target_num_reads": 0,
                "genome_size": 4600000,
                "target_depth": 250,
            },
        ),
        (
            {"method": "random"},
            {"method": "random", "target_num_reads": 0, "genome_size": 0, "target_depth": 150},
        ),
        ({}, {"method": "none", "target_num_reads": 0, "genome_size": 0, "target_depth": 150}),
    ],
)
def test_downsample_settings_update(data, expected):
    downsample_settings = DownsampleSettings()
    downsample_settings = downsample_settings.update(data)
    assert downsample_settings.model_dump() == expected


def test_downsample_settings_update_extra_keys():
    message = r"Extra field\(s\): INVALID"
    with pytest.raises(DownsampleSettingsError, match=message):
        downsample_settings = DownsampleSettings()
        downsample_settings = downsample_settings.update({"INVALID": "INVALID"})


@pytest.mark.parametrize(
    "data,expected",
    [
        (
            {"filter": {"enabled": False}, "downsample": {"method": "bbnorm"}},
            {
                "filter": {"enabled": False, "min_length": 100, "quality": 15},
                "downsample": {
                    "method": "bbnorm",
                    "target_num_reads": 0,
                    "genome_size": 0,
                    "target_depth": 150,
                },
            },
        ),
        (
            {"filter": {"enabled": False}},
            {
                "filter": {"enabled": False, "min_length": 100, "quality": 15},
                "downsample": {
                    "method": "none",
                    "target_num_reads": 0,
                    "genome_size": 0,
                    "target_depth": 150,
                },
            },
        ),
        (
            {"downsample": {"method": "bbnorm"}},
            {
                "filter": {"enabled": True, "min_length": 100, "quality": 15},
                "downsample": {
                    "method": "bbnorm",
                    "target_num_reads": 0,
                    "genome_size": 0,
                    "target_depth": 150,
                },
            },
        ),
        (
            {},
            {
                "filter": {"enabled": True, "min_length": 100, "quality": 15},
                "downsample": {
                    "method": "none",
                    "target_num_reads": 0,
                    "genome_size": 0,
                    "target_depth": 150,
                },
            },
        ),
    ],
)
def test_global_settings_parse_data(data, expected):
    global_settings = GlobalSettings.parse_data(data)
    assert global_settings.model_dump() == expected


def test_global_settings_parse_data_extra_keys():
    message = r"Extra inputs are not permitted \[type=extra_forbidden, input_value='INVALID'"
    with pytest.raises(ValidationError, match=message):
        GlobalSettings.parse_data({"INVALID": "INVALID"})
