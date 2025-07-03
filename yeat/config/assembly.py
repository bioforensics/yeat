# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from dataclasses import dataclass
from sys import platform
from typing import Optional


ALGORITHMS = {
    "spades": ["paired", "single"],
    "megahit": ["paired", "single"],
    "unicycler": ["paired", "single", "ont", "pacbio", "hybrid"],
    "canu": ["ont", "pacbio"],
    "flye": ["ont", "pacbio"],
    "hifiasm": ["pacbio"],
    "hifiasm_meta": ["pacbio"],
    "metamdbg": ["pacbio"],
    "penguin": ["paired", "single"],
    "velvet": ["paired", "single"],
}
MODE = ["paired", "single", "ont", "pacbio", "hybrid"]


@dataclass
class Assembly:
    algorithm: str
    mode: str
    extra_args: Optional[str] = None
    samples: Optional[list] = None

    def __post_init__(self):
        self.check_input_data()
        self.check_mode_matches_algorithm()
        self.check_metaMDBG_OS()
        # self.check_canu_required_params()

    def __str__(self):
        return f'''algorithm = "{self.algorithm}"
mode = "{self.mode}"'''

    def check_input_data(self):
        if self.algorithm not in ALGORITHMS:
            raise "Invalid assembly algorithm"
        if self.mode not in MODE:
            raise "Invalid mode"

    def check_mode_matches_algorithm(self):
        if self.mode not in ALGORITHMS[self.algorithm]:
            raise "Mode does not match algorithm"

    def check_metaMDBG_OS(self):
        if self.algorithm == "metamdbg" and platform not in ["linux", "linux2"]:
            raise "metaMDBG can only run on 'Linux OS'"

    def check_canu_required_params(self):
        if "genomeSize=" not in self.extra_args:
            raise f"Canu requires extra argument 'genomeSize'"
        # if self.threads < 4:
        #     raise "Canu requires at least 4 avaliable cores; increase '-t' or '--threads' to 4 or more"

    def get_target_files(self):
        return f"yeat/{self.algorithm}/contigs.fasta"


#     def get_target_files(self):
#         target_files = []
#         for sample in self.samples.values():
#             target_files.append(self.get_qa_file(sample))
#         return target_files

#     def get_qa_file(self, sample):
#         readtype = self.get_readtype(sample)
#         algorithm_dir = f"analysis/{sample.label}/{readtype}/{self.label}/{self.algorithm}"
#         if self.bandage and self.algorithm != "penguin":
#             return f"{algorithm_dir}/bandage/.done"
#         return f"{algorithm_dir}/quast/report.html"
