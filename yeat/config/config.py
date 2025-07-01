# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .assembly import Assembly
from .sample import Sample
from dataclasses import dataclass
from io import StringIO
from typing import Dict


@dataclass
class Config:
    samples: Dict[str, Sample]
    assemblies: Dict[str, Assembly]

    def __post_init__(self):
        # print("in constructor")

        # self.target_files = []
        pass

    def __str__(self):
        output = StringIO()
        for sample_label, sample in self.samples.items():
            print(f"[sample.{sample_label}]\n{sample}\n", file=output)
        for assembly_label, assembly in self.assemblies.items():
            print(f"[assemblies.{assembly_label}]\n{assembly}\n", file=output)
        return output.getvalue().strip()

    def get_target_files(self, workdir):
        target_files = []
        for sample_label, sample in self.samples.items():
            for target_file in sample.get_target_files():
                target_files.append(f"analysis/{sample_label}/{target_file}")
        # for assembly_label, assembly in self.assemblies.items():
        #     print(assembly.get_target_files())
        return target_files


#     def check_sample_readtypes_match_assembly_mode(self):
#         for sample in self.samples.values():
#             if not self.mode_and_readtypes_are_compatible(sample):
#                 message = f"No readtypes in '{sample.label}' match '{self.label}' assembly mode '{self.mode}'"
#                 raise AssemblyConfigError(message)

#     def get_target_files(self):
#         target_files = []
#         for element in chain(self.samples.values(), self.assemblies.values()):
#             target_files += element.target_files
#         return target_files
