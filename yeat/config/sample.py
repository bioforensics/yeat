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
from typing import Dict, Optional


class Sample(BaseModel):
    label: str
    data: Dict
    downsample: Optional[int] = -1
    genome_size: Optional[
        int
    ] = 0  # fix up these fixed values; overwrite them if cli value changed
    coverage_depth: Optional[int] = 150

    def input_paths(self):
        for seqtype, seqpath in self.data.items():
            path = Path(seqpath)
            seqpaths = path.parent.glob(path.name)
            yield from seqpaths

    def best_long_read_paths(self):
        if not self.has_long_reads:
            raise SampleConfigurationError(f"sample {self.label} isn't configured with long reads")
        for read_type in ("pacbio_hifi", "ont_duplex", "ont_simplex"):
            if read_type in self.data:
                return self.input_paths(seqtypes={read_type})

    @property
    def target_files(self):
        fastqs = list(self.input_paths())
        # readtype = has_blah()
        if len(fastqs) == 1:  # how to deal with hybrid samples? #deal with different read types
            return [f"analysis/{self.label}/qc/illumina/fastqc/read_fastqc.html"]
        else:
            fastq_paths = [
                f"analysis/{self.label}/qc/illumina/fastqc/R1_fastqc.html",
                f"analysis/{self.label}/qc/illumina/fastqc/R2_fastqc.html",
            ]
            return fastq_paths

    @property
    def has_illumina(self):
        return "illumina" in self.data

    @property
    def has_pacbio(self):
        return "pacbio_hifi" in self.data

    @property
    def has_ont(self):
        return "ont_simplex" in self.data or "ont_duplex" in self.data


class SampleConfigurationError(ValueError):
    pass
