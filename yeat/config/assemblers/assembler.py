# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from ..sample import Sample
from pydantic import BaseModel
from typing import Dict, Optional


class Assembler(BaseModel):
    label: str
    arguments: Optional[str] = None
    samples: Dict[str, Sample]

    @classmethod
    def parse_data(cls, label, data, samples):
        arguments = data["arguments"] if "arguments" in data else None
        s = cls.select_samples(data, samples)
        return cls(label=label, arguments=arguments, samples=s)

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
