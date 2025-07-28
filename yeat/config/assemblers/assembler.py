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


REQUIRED_KEYS = {"algorithm"}
OPTIONAL_KEYS = {"arguments", "samples"}


class Assembler(BaseModel):
    label: str
    arguments: Optional[str] = None
    samples: Dict[str, Sample]

    @classmethod
    def parse_data(cls, label, data, samples):
        arguments = data["arguments"] if "arguments" in data else None
        s = cls._select_samples(data, samples)
        return cls(label=label, arguments=arguments, samples=s)

    @classmethod
    def _select_samples(cls, data, samples):
        s = data.get("samples", samples)
        return {
            label: sample for label, sample in s.items() if cls._check_sample_compatibility(sample)
        }

    @property
    def extra_args(self):
        return self.arguments or ""
