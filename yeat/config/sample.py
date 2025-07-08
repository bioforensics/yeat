# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pathlib import Path
from pydantic import BaseModel
from typing import Dict


class Sample(BaseModel):
    label: str
    data: Dict

    def input_paths(self):
        for seqtype, seqpath in self.data.items():
            path = Path(seqpath)
            seqpaths = path.parent.glob(path.name)
            yield from seqpaths

    @property
    def target_files(self):
        fastqs = list(self.input_paths())
        print(fastqs)
        print("here!!!!")
        return []
