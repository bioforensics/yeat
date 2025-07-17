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


ONT_PLATFORMS = {"ont_simplex", "ont_duplex"}
READ_TYPES = {"illumina", "pacbio_hifi"}.union(ONT_PLATFORMS)
OPTIONAL_KEYS = {
    "coverage_depth",
    "downsample",
    "genome_size",
    "min_length",
    "quality",
    "skip_filter",
}
VALID_KEYS = READ_TYPES.union(OPTIONAL_KEYS)
BEST_LR_ORDER = ("pacbio_hifi", "ont_duplex", "ont_simplex")


class Sample(BaseModel):
    label: str
    data: Dict

    @classmethod
    def parse_data(cls, label, data, flags):
        keys = set(data.keys())
        cls._check_required_keys(keys)
        cls._check_optional_keys(keys)
        # if len(reads) not in (1, 2):
        #     raise ValueError(f"expected 1 or 2 FASTQ files, not {len(reads)}")
        cls._expand_read_paths_in_dict(data)
        cls._add_default_flag_values(data, flags)
        return cls(label=label, data=data)

    @staticmethod
    def _check_required_keys(keys):
        intersection_list = list(keys & READ_TYPES)
        if len(intersection_list) == 0:
            raise (SampleConfigurationError("need to add read data to sample!"))

    @staticmethod
    def _check_optional_keys(keys):
        elements_only_in_list1 = list(keys.difference(VALID_KEYS))
        if len(elements_only_in_list1) > 0:
            raise (SampleConfigurationError("found unrecongizable keys!"))

    @staticmethod
    def _expand_read_paths_in_dict(data):
        for key, value in data.items():
            if key in READ_TYPES:
                data[key] = list(Sample._expand_glob_pattern(value))

    @staticmethod
    def _expand_glob_pattern(read_path):
        path = Path(read_path)
        seq_paths = path.parent.glob(path.name)
        yield from seq_paths

    @staticmethod
    def _add_default_flag_values(data, flags):
        for key in OPTIONAL_KEYS:
            if key not in data:
                data[key] = flags[key]

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
        return self.has_pacbio or self.has_ont

    @property
    def has_both_short_and_long_reads(self):
        return self.has_illumina and self.has_long_reads

    @property
    def downsample(self):
        return self.data.get("downsample", -1)

    @property
    def genome_size(self):
        return self.data.get("genome_size", 0)

    @property
    def coverage_depth(self):
        return self.data.get("coverage_depth", 150)

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
    def target_files(self):
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

    @property
    def best_long_read_type(self):
        for read_type in BEST_LR_ORDER:
            if read_type in self.data:
                return read_type


class SampleConfigurationError(ValueError):
    pass
