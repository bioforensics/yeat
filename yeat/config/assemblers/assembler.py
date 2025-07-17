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
VALID_KEYS = REQUIRED_KEYS.union(OPTIONAL_KEYS)


class Assembler(BaseModel):
    label: str
    arguments: Optional[str] = None
    samples: Dict[str, Sample]

    @classmethod
    def parse_data(cls, label, data, samples):
        keys = set(data.keys())
        cls._check_required_keys(keys)
        cls._check_optional_keys(keys)
        arguments = data["argument"] if "argument" in data else None
        s = cls._select_samples(cls, data, samples)
        return cls(label=label, arguments=arguments, samples=s)

    @staticmethod
    def _check_required_keys(keys):
        intersection_list = list(keys & REQUIRED_KEYS)
        if len(intersection_list) == 0:
            raise (
                AssemblerConfigurationError("algorithm missing from [assemblers] configuration")
            )

    @staticmethod
    def _check_optional_keys(keys):
        elements_only_in_list1 = list(keys.difference(VALID_KEYS))
        if len(elements_only_in_list1) > 0:
            raise (AssemblerConfigurationError("found unrecongizable keys!"))

    @staticmethod
    def _select_samples(cls, data, samples):
        s = data.get("samples", samples)
        return {
            label: sample for label, sample in s.items() if cls._check_sample_compatibility(sample)
        }

    @property
    def extra_args(self):
        return self.arguments or ""

    # def input_files(self, sample, algorithm, read_type):
    #     temp = self.samples[sample].data[read_type]
    #     if len(temp) == 1:
    #         return [f"analysis/{sample}/qc/{algorithm}/downsample/read.fastq.gz"]
    #     else:
    #         r1=f"analysis/{sample}/qc/{algorithm}/downsample/R1.fastq.gz"
    #         r2=f"analysis/{sample}/qc/{algorithm}/downsample/R2.fastq.gz"
    #         return [r1, r2]


class AssemblerConfigurationError(ValueError):
    pass
