# -------------------------------------------------------------------------------------------------
# Copyright (c) 2026, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from copy import deepcopy
from pydantic import ValidationError
import pytest
from yeat.config.downsample_settings import DownsampleSettings, DownsampleSettingsError
from yeat.config.filter_settings import FilterSettings, FilterSettingsError
from yeat.config.global_settings import GlobalSettings


GLOBAL_DEFAULT_SETTINGS = {
    "filter": {
        "short_filter_settings": {"enabled": False, "fastp_args": ""},
        "long_filter_settings": {"enabled": False, "chopper_args": ""},
    },
    "downsample": {
        "short_downsample_settings": {
            "enabled": False,
            "method": "random",
            "target_depth": 150,
            "target_num_reads": "auto",
            "genome_size": "auto",
        },
        "long_downsample_settings": {
            "enabled": False,
            "target_depth": 150,
            "target_num_reads": "auto",
            "genome_size": "auto",
        },
    },
}


@pytest.mark.parametrize(
    "data",
    [
        GLOBAL_DEFAULT_SETTINGS,
        {"filter": GLOBAL_DEFAULT_SETTINGS["filter"]},
        {
            "filter": {
                "short_filter_settings": GLOBAL_DEFAULT_SETTINGS["filter"]["short_filter_settings"]
            }
        },
        {
            "filter": {
                "long_filter_settings": GLOBAL_DEFAULT_SETTINGS["filter"]["long_filter_settings"]
            }
        },
        {"downsample": GLOBAL_DEFAULT_SETTINGS["downsample"]},
        {
            "downsample": {
                "short_downsample_settings": GLOBAL_DEFAULT_SETTINGS["downsample"][
                    "short_downsample_settings"
                ]
            }
        },
        {
            "downsample": {
                "long_downsample_settings": GLOBAL_DEFAULT_SETTINGS["downsample"][
                    "long_downsample_settings"
                ]
            }
        },
        {},
    ],
)
def test_global_settings_parse_data(data):
    GLOBAL_DEFAULT_SETTINGS_copy = deepcopy(GLOBAL_DEFAULT_SETTINGS)
    global_settings = GlobalSettings.parse_data(GLOBAL_DEFAULT_SETTINGS_copy)
    assert global_settings.model_dump() == GLOBAL_DEFAULT_SETTINGS


@pytest.mark.parametrize(
    "update_method, attr_path, initial_expected, update_payload, final_expected",
    [
        (
            "update_filter_settings",
            ("filter", "short_filter_settings"),
            {"enabled": False, "fastp_args": ""},
            {
                "short": {
                    "enabled": True,
                    "fastp_args": "--length_required 100 --unqualified_percent_limit 25",
                }
            },
            {
                "enabled": True,
                "fastp_args": "--length_required 100 --unqualified_percent_limit 25",
            },
        ),
        (
            "update_filter_settings",
            ("filter", "long_filter_settings"),
            {"enabled": False, "chopper_args": ""},
            {"long": {"enabled": True, "chopper_args": "--quality 15 --minlength 250"}},
            {"enabled": True, "chopper_args": "--quality 15 --minlength 250"},
        ),
        (
            "update_downsample_settings",
            ("downsample", "short_downsample_settings"),
            {
                "enabled": False,
                "target_depth": 150,
                "target_num_reads": "auto",
                "genome_size": "auto",
                "method": "random",
            },
            {"short": {"enabled": True, "method": "bbnorm"}},
            {
                "enabled": True,
                "target_depth": 150,
                "target_num_reads": "auto",
                "genome_size": "auto",
                "method": "bbnorm",
            },
        ),
        (
            "update_downsample_settings",
            ("downsample", "long_downsample_settings"),
            {
                "enabled": False,
                "target_depth": 150,
                "target_num_reads": "auto",
                "genome_size": "auto",
            },
            {"long": {"enabled": True}},
            {
                "enabled": True,
                "target_depth": 150,
                "target_num_reads": "auto",
                "genome_size": "auto",
            },
        ),
    ],
)
def test_update_settings(
    update_method, attr_path, initial_expected, update_payload, final_expected
):
    settings = GlobalSettings.parse_data(deepcopy(GLOBAL_DEFAULT_SETTINGS))
    obj = settings
    for attr in attr_path:
        obj = getattr(obj, attr)
    assert obj.model_dump() == initial_expected
    getattr(settings, update_method)(update_payload)
    obj = settings
    for attr in attr_path:
        obj = getattr(obj, attr)
    assert obj.model_dump() == final_expected


@pytest.mark.parametrize(
    "model",
    [GlobalSettings, FilterSettings, DownsampleSettings],
)
def test_parse_data_extra_keys(model):
    message = r"Extra inputs are not permitted \[type=extra_forbidden, input_value='INVALID'"
    with pytest.raises(ValidationError, match=message):
        model.parse_data({"INVALID": "INVALID"})


@pytest.mark.parametrize(
    "model,error_model",
    [(FilterSettings, FilterSettingsError), (DownsampleSettings, DownsampleSettingsError)],
)
def test_update_extra_keys(model, error_model):
    message = r"Extra field\(s\): INVALID"
    m = model()
    with pytest.raises(error_model, match=message):
        m.update({"INVALID": "INVALID"})
