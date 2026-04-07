# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .global_settings import GlobalSettings, FilterSettings, DownsampleSettings
from copy import deepcopy
from pathlib import Path
from pydantic import BaseModel, field_validator
from typing import Dict


ONT_PLATFORMS = {"ont_simplex", "ont_duplex", "ont_ultralong"}
READ_TYPES = ONT_PLATFORMS | {"illumina", "pacbio_hifi"}
BEST_LR_ORDER = ("pacbio_hifi", "ont_duplex", "ont_simplex", "ont_ultralong")
OPTIONAL_KEYS = {"filter", "downsample"}


class Sample(BaseModel):
    label: str
    data: Dict[str, list[Path]]
    filter_settings: FilterSettings
    downsample_settings: DownsampleSettings

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
    def has_valid_downsample_application(cls, data):
        if "illumina" not in data and data["method"] == "bbnorm":
            raise SampleConfigurationError(f"BBNorm can only be applied to Illumina reads")
        return data

    @field_validator("data")
    @classmethod
    def has_invalid_keys(cls, data):
        extra_keys = data - GlobalSettings.model_fields.keys() - READ_TYPES
        if extra_keys:
            raise SampleConfigurationError(f"Sample has unexpected key(s): {extra_keys}")
        return data

    @classmethod
    def parse_data(cls, label, data, global_settings):
        filter_copy = deepcopy(global_settings.filter).update(data.get("filter", {}))
        downsample_copy = deepcopy(global_settings.downsample).update(data.get("downsample", {}))
        data.pop("filter", None)
        data.pop("downsample", None)
        return cls(
            label=label,
            data=data,
            filter_settings=filter_copy,
            downsample_settings=downsample_copy,
        )

    @staticmethod
    def _add_global_settings(data, global_settings):
        for key, value in global_settings.model_dump().items():
            if key not in data:
                data[key] = value

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

    @property
    def enabled(self):
        return self.filter_settings.enabled

    @property
    def min_length(self):
        return self.filter_settings.min_length

    @property
    def quality(self):
        return self.filter_settings.quality

    @property
    def method(self):
        return self.downsample_settings.method

    @property
    def target_num_reads(self):
        return self.downsample_settings.target_num_reads

    @property
    def genome_size(self):
        return self.downsample_settings.genome_size

    @property
    def target_depth(self):
        return self.downsample_settings.target_depth

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
