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
        keys = set(data.keys())
        cls._check_required_keys(keys)
        cls._check_optional_keys(keys)
        arguments = data["arguments"] if "arguments" in data else None
        s = cls._select_samples(cls, data, samples)
        return cls(label=label, arguments=arguments, samples=s)

    @staticmethod
    def _check_required_keys(keys):
        intersection = list(keys & REQUIRED_KEYS)
        if len(intersection) != len(REQUIRED_KEYS):
            raise (AssemblerConfigurationError(f"YEAT assembler must include {REQUIRED_KEYS}"))

    @staticmethod
    def _check_optional_keys(keys):
        valid_keys = REQUIRED_KEYS.union(OPTIONAL_KEYS)
        invalid_keys = list(keys.difference(valid_keys))
        if invalid_keys:
            raise (
                AssemblerConfigurationError(
                    f"YEAT assembler has unrecognizable keys {invalid_keys}"
                )
            )

    @staticmethod
    def _select_samples(cls, data, samples):
        s = data.get("samples", samples)
        return {
            label: sample for label, sample in s.items() if cls._check_sample_compatibility(sample)
        }

    @property
    def extra_args(self):
        return self.arguments or ""


class AssemblerConfigurationError(ValueError):
    pass
