# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from ..sample import Sample
from pydantic import BaseModel, field_validator
from typing import Optional, Dict


class Assembler(BaseModel):
    label: str
    arguments: Optional[str]
    samples: Dict[str, Sample]

    @field_validator("samples")
    @classmethod
    def has_one_sample(cls, samples):
        if not samples:
            message = f"{cls.__name__} has no samples to work with"
            raise AssemblerConfigurationError(message)
        return samples

    @classmethod
    def parse_data(cls, label, data, samples):
        arguments = data.get("arguments")
        selected_samples = cls.select_samples(data, samples)
        return cls(label=label, arguments=arguments, samples=selected_samples)

    @classmethod
    def select_samples(cls, data, samples):
        compatible_samples = dict()
        requested_samples = data.get("samples", samples)
        for sample_name in requested_samples:
            if sample_name not in samples:
                message = f"Sample '{sample_name}' not found in provided samples"
                raise AssemblerConfigurationError(message)
            sample = samples[sample_name]
            if cls._check_sample_compatibility(sample):
                compatible_samples[sample_name] = sample
        return compatible_samples

    @property
    def extra_args(self):
        return self.arguments or ""


class AssemblerConfigurationError(ValueError):
    pass
