# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .downsample_settings import DownsampleGroup
from .filter_settings import FilterGroup
from .global_settings import GlobalSettings
from pathlib import Path
from pydantic import BaseModel, field_validator, model_validator
from typing import Dict


ONT_PLATFORMS = {"ont_simplex", "ont_duplex", "ont_ultralong"}
READ_TYPES = ONT_PLATFORMS | {"illumina", "pacbio_hifi"}
BEST_LR_ORDER = ("pacbio_hifi", "ont_duplex", "ont_simplex", "ont_ultralong")


class Sample(BaseModel):
    label: str
    data: Dict[str, list[Path]]
    filter: FilterGroup
    downsample: DownsampleGroup

    @field_validator("data")
    @classmethod
    def has_one_read_type(cls, data):
        if not data.keys() & READ_TYPES:
            raise SampleConfigurationError("Sample must have at least one read type")
        return data

    @field_validator("data")
    @classmethod
    def has_read_paths(cls, data):
        for read_type, read_paths in data.items():
            if read_type not in READ_TYPES:
                continue
            if not read_paths:
                message = f"Unable to find FASTQ files for sample"
                raise SampleConfigurationError(message)
            if len(read_paths) > 2:
                message = f"Sample has too many FASTQ files. Expected at most 2, found {len(read_paths)}."
                raise SampleConfigurationError(message)
        return data

    @field_validator("data")
    @classmethod
    def has_invalid_keys(cls, data):
        extra_keys = set(data.keys()) - READ_TYPES - set(GlobalSettings.model_fields.keys())
        if extra_keys:
            raise SampleConfigurationError(f"Sample has unexpected key(s): {extra_keys}")
        return data

    @classmethod
    def parse_data(cls, label, data, global_settings):
        global_settings_copy = global_settings.model_copy()
        global_settings_copy.update_filter_settings(data.get("filter", {}))
        global_settings_copy.update_downsample_settings(data.get("downsample", {}))
        data.pop("filter", None)
        data.pop("downsample", None)
        return cls(
            label=label,
            data=data,
            filter=global_settings_copy.filter,
            downsample=global_settings_copy.downsample,
        )

    @model_validator(mode="after")
    def has_valid_downsample_application(self):
        if "illumina" not in self.data and self.downsample_settings.method == "bbnorm":
            raise SampleConfigurationError("BBNorm can only be applied to Illumina reads")
        return self

    @property
    def has_illumina(self):
        return "illumina" in self.data

    @property
    def has_ont(self):
        return any(key in ONT_PLATFORMS for key in self.data)

    @property
    def has_pacbio(self):
        return "pacbio_hifi" in self.data

    @property
    def has_long_reads(self):
        return self.has_ont or self.has_pacbio

    @property
    def best_long_read_type(self):
        for read_type in BEST_LR_ORDER:
            if read_type in self.data:
                return read_type
        return None

    def get_filter_settings(self, read_type):
        return getattr(self.filter, f"{read_type}_filter_settings")

    def get_downsample_settings(self, read_type):
        return getattr(self.downsample, f"{read_type}_downsample_settings")

    def filter_enabled(self, read_type):
        return self.get_filter_settings(read_type).enabled

    def filter_args(self, read_type):
        settings = self.get_filter_settings(read_type)
        return settings.fastp_args if read_type == "short" else settings.chopper_args

    def downsample_enabled(self, read_type):
        return self.get_downsample_settings(read_type).enabled

    def downsample_method(self, read_type):
        return self.get_downsample_settings(read_type).method

    def target_depth(self, read_type):
        return self.get_downsample_settings(read_type).target_depth

    def target_num_reads(self, read_type):
        return self.get_downsample_settings(read_type).target_num_reads

    def genome_size(self, read_type):
        return self.get_downsample_settings(read_type).genome_size

    @property
    def targets(self):
        fastq_paths = list()
        for read_type in READ_TYPES:
            if read_type not in self.data:
                continue
            fastqs = self.data[read_type]
            fastqc_dir = f"analysis/{self.label}/qc/{read_type}/fastqc"
            if len(fastqs) == 2:
                fastq_paths.append(f"{fastqc_dir}/R1_fastqc.html")
                fastq_paths.append(f"{fastqc_dir}/R2_fastqc.html")
                continue
            fastq_paths.append(f"{fastqc_dir}/read_fastqc.html")
        return fastq_paths


class SampleConfigurationError(ValueError):
    pass
