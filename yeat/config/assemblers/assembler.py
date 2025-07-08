# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pydantic import BaseModel
from typing import Optional


class Assembler(BaseModel):
    label: str
    arguments: Optional[str] = None
    samples: Optional[list] = None

    @classmethod
    def parse_data(cls, label, assembler_data):
        # if "samples" in assembly:
        #     # This block restricts an assembler to a list of user-specified samples if provided in
        #     # the corresponding "assembler" block in the config .toml file. If not provided,
        #     # assembler is applied to all samples with compatible reads.
        #     #
        #     # Each *Assembler class specifies its own `.compatible_samples` method.
        #     samples = {
        #         label: sample for label, sample in samples.items() if label in assembly["samples"]
        #     }
        arguments = assembler_data["argument"] if "argument" in assembler_data else None
        samples = assembler_data["samples"] if "sample" in assembler_data else None
        return cls(label=label, arguments=arguments, samples=samples)
    
    @property
    def extra_args(self):
        return "" if self.arguments is None else self.arguments
    
    @property
    def override_samples(self):
        return sorted(self._samples.keys())
    
    @property
    def target_files(self):
        return []
