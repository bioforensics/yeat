# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .global_settings import GlobalSettings
from pathlib import Path
from pydantic import BaseModel, field_validator
from typing import Dict, Union


ONT_PLATFORMS = {"ont_simplex", "ont_duplex", "ont_ultralong"}
READ_TYPES = ONT_PLATFORMS | {"illumina", "pacbio_hifi"}
BEST_LR_ORDER = ("pacbio_hifi", "ont_duplex", "ont_simplex", "ont_ultralong")


class Sample(BaseModel):
    label: str
    data: Dict[str, Union[list[Path], int, bool]]

    @field_validator("data")
    @classmethod
    def has_one_read_type(cls, data):
        if not data.keys() & READ_TYPES:
            raise SampleConfigurationError("Sample must have at least one read type")
        return data

    @field_validator("data")
    @classmethod
    def has_valid_keys(cls, data):
        field_names = set(GlobalSettings.model_fields.keys())
        valid_keys = field_names | READ_TYPES
        extra_keys = set(data.keys()) - valid_keys
        if extra_keys:
            raise SampleConfigurationError(f"Sample has unexpected key(s): {extra_keys}")
        return data

    @classmethod
    def parse_data(cls, label, data, global_settings):
        cls._check_read_paths(label, data)
        cls._add_global_settings(data, global_settings)
        return cls(label=label, data=data)

    @staticmethod
    def _check_read_paths(label, data):
        for read_type, read_paths in data.items():
            if read_type not in READ_TYPES:
                continue
            reads = sorted(read_paths)
            if not reads:
                message = f"Unable to find FASTQ files for sample '{label}' at path: {read_paths}"
                raise SampleConfigurationError(message)
            if len(reads) > 2:
                message = (
                    f"Found too many FASTQ files for sample '{label}' at path: {read_paths}. "
                    f"Expected at most 2, found {len(reads)}."
                )
                raise SampleConfigurationError(message)
            data[read_type] = reads

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
    def target_coverage_depth(self):
        return self.data.get("target_coverage_depth", 150)

    @property
    def target_num_reads(self):
        return self.data.get("target_num_reads", -1)

    @property
    def genome_size(self):
        return self.data.get("genome_size", 0)

    @property
    def min_length(self):
        return self.data.get("min_length", 100)

    @property
    def quality(self):
        return self.data.get("quality", 10)

    @property
    def skip_filter(self):
        return self.data.get("skip_filter", True)

    @property
    def best_long_read_type(self):
        for read_type in BEST_LR_ORDER:
            if read_type in self.data:
                return read_type
        return None

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
