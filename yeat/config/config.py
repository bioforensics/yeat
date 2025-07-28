# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .assemblers import select
from .assemblers.assembler import Assembler
from .global_settings import GlobalSettings
from .sample import Sample
from pydantic import BaseModel
from typing import Dict


class AssemblyConfiguration(BaseModel):
    global_settings: GlobalSettings
    samples: Dict[str, Sample]
    assemblers: Dict[str, Assembler]

    @classmethod
    def parse_snakemake_config(cls, config):
        global_settings = GlobalSettings.parse_data(config["global_settings"])
        samples = cls._parse_samples(config, global_settings)
        assemblers = cls._parse_assemblers(config, samples)
        return cls(global_settings=global_settings, samples=samples, assemblers=assemblers)

    @staticmethod
    def _parse_samples(config, global_settings):
        samples = dict()
        for label, data in config["samples"].items():
            samples[label] = Sample.parse_data(label, data, global_settings)
        return samples

    @staticmethod
    def _parse_assemblers(config, samples):
        assemblers = dict()
        for label, data in config["assemblers"].items():
            assembler_class = select(data["algorithm"])
            assemblers[label] = assembler_class.parse_data(label, data, samples)
        return assemblers

    @property
    def targets(self):
        targets = list()
        for sample in self.samples.values():
            targets.extend(sample.targets)
        for assembler in self.assemblers.values():
            targets.extend(assembler.targets)
        return targets
