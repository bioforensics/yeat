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
    samples: Dict[str, Sample]
    arguments: Optional[str] = None

    @classmethod
    def parse_data(cls, label, assembler_data, samples):
        if "samples" in assembler_data:
            samples = {
                label: sample
                for label, sample in samples.items()
                if label in assembler_data["samples"]
            }
        arguments = assembler_data["argument"] if "argument" in assembler_data else None
        return cls(label=label, arguments=arguments, samples=samples)

    @property
    def extra_args(self):
        return "" if self.arguments is None else self.arguments

    # @property
    # def target_files(self):
    #     quast_files = [
    #         f"analysis/{sample}/yeat/{self.label}/quast/report.html"
    #         for sample in self.samples
    #     ]
    #     return sorted(quast_files)
