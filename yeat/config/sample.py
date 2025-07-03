# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from dataclasses import dataclass, fields
from pathlib import Path
from typing import Optional, Union, List, Dict


@dataclass
class Sample:
    illumina: Optional[Union[List[str], str]] = None
    simplex: Optional[str] = None
    duplex: Optional[str] = None
    ultra_long: Optional[str] = None
    hifi: Optional[str] = None
    # update these variables here based on CLI!!! if cli is filled out, override toml
    downsample: Optional[int] = -1
    genome_size: Optional[int] = -1
    coverage_depth: Optional[int] = -1

    def __str__(self):
        return "\n".join(f"{field.name}: {getattr(self, field.name)}" for field in fields(self))

    def get_target_files(self):
        target_files = []
        if self.illumina:
            if isinstance(self.illumina, list):
                target_files.append("qc/illumina/fastqc/R1_fastqc.html")
                target_files.append("qc/illumina/fastqc/R2_fastqc.html")
            else:
                target_files.append("qc/illumina/fastqc/read_fastqc.html")
        for read_type in ["simplex", "duplex", "ultra_long", "hifi"]:
            if getattr(self, read_type):
                target_files.append(f"qc/{read_type}/fastqc/read_fastqc.html")
        return target_files
