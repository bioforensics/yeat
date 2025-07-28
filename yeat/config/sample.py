# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pathlib import Path, PosixPath
from pydantic import BaseModel
from typing import Dict, Union


ONT_PLATFORMS = {"ont_simplex", "ont_duplex"}
READ_TYPES = ONT_PLATFORMS | {"illumina", "pacbio_hifi"}
BEST_LR_ORDER = ("pacbio_hifi", "ont_duplex", "ont_simplex")


class Sample(BaseModel):
    label: str
    data: Dict[str, Union[list[PosixPath], int, bool]]

    @classmethod
    def parse_data(cls, label, data, global_settings):
        cls._expand_read_paths(data)
        cls._add_global_settings(data, global_settings)
        return cls(label=label, data=data)

    @staticmethod
    def _expand_read_paths(data):
        for read_type, read_path in data.items():
            data[read_type] = list(Sample._expand_glob_pattern(Path(read_path)))

    @staticmethod
    def _expand_glob_pattern(read_path):
        yield from read_path.parent.glob(read_path.name)

    @staticmethod
    def _add_global_settings(data, global_settings):
        for key, value in global_settings.dict().items():
            if key not in data:
                data[key] = value

    @property
    def has_illumina(self):
        return "illumina" in self.data

    @property
    def has_ont(self):
        return any(key in ONT_PLATFORMS for key in self.data)

    @property
    def has_pacbio(self):
        return "pacbio_hifi" in self.data

    @property
    def has_long_reads(self):
        return self.has_ont or self.has_pacbio

    @property
    def has_both_short_and_long_reads(self):
        return self.has_illumina and self.has_long_reads

    @property
    def coverage_depth(self):
        return self.data.get("coverage_depth", 150)

    @property
    def downsample(self):
        return self.data.get("downsample", -1)

    @property
    def genome_size(self):
        return self.data.get("genome_size", 0)

    @property
    def min_length(self):
        return self.data.get("min_length", 100)

    @property
    def quality(self):
        return self.data.get("quality", 10)

    @property
    def skip_filter(self):
        return self.data.get("skip_filter", False)

    @property
    def best_long_read_type(self):
        for read_type in BEST_LR_ORDER:
            if read_type in self.data:
                return read_type

    @property
    def targets(self):
        fastq_paths = list()
        for read_type in READ_TYPES:
            if read_type not in self.data:
                continue
            fastqs = self.data[read_type]
            fastqc_dir = f"analysis/{self.label}/qc/{read_type}/fastqc"
            if len(fastqs) == 2:
                fastq_paths.append(f"{fastqc_dir}/R1_fastqc.html")
                fastq_paths.append(f"{fastqc_dir}/R2_fastqc.html")
                continue
            fastq_paths.append(f"{fastqc_dir}/read_fastqc.html")
        return fastq_paths
