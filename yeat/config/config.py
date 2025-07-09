# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .assemblers import select
from .sample import Sample
from pydantic import BaseModel
from typing import Dict


class AssemblyConfiguration(BaseModel):
    samples: Dict
    assemblers: Dict

    @classmethod
    def parse_toml(cls, config_data):
        cls._check_required_input_data(config_data)
        samples = cls._parse_samples(config_data)
        print(samples)
        assert 0
        assemblers = cls._parse_assemblers(config_data, samples)
        config = cls(samples=samples, assemblers=assemblers)
        return config

    @staticmethod
    def _check_required_input_data(config_data):
        if "samples" not in config_data:
            raise ConfigurationError("YEAT configuration must include [samples]")
        if "assemblers" not in config_data:
            raise ConfigurationError("YEAT configuration must include [assemblers]")
        for assembler_data in config_data["assemblers"].values():
            if "algorithm" not in assembler_data:
                raise ConfigurationError("algorithm missing from [assemblers] configuration")

    @staticmethod
    def _parse_samples(config_data):
        samples = dict()
        for label, sample_data in config_data["samples"].items():
            samples[label] = Sample(label=label, data=sample_data)
        return samples

    @staticmethod
    def _parse_assemblers(config_data, samples):
        assemblers = dict()
        for label, assembler_data in config_data["assemblers"].items():
            assembler_class = select(assembler_data["algorithm"])
            assembler = assembler_class.parse_data(label, assembler_data, samples)
            assemblers[label] = assembler
        return assemblers

    @property
    def assembly_targets(self):
        targets = list()
        for sample in self.samples.values():
            targets.extend(sample.target_files)
        print(targets)
        assert 0
        # for assembler in self.assemblers.values():
        #     targets.extend(assembler.quast_files())
        return targets

    def input_files(self, sample, seqtypes=None):
        if sample not in self.samples:
            raise ConfigurationError(f"sample {sample} not found")
        # paths = self.samples[sample].input_paths(seqtypes)
        paths = self.samples[sample].input_paths()
        return list(paths)

    # def spades_input(self, sample):
    #     return self.samples[sample].fastp_targets

    # def unicycler_input(self, sample):
    #     return self.samples[sample].hybrid_inputs

    # def hifiasm_meta_input(self, sample):
    #     return self.samples[sample].input_paths(seqtypes={"pacbio_hifi"})


class ConfigurationError(ValueError):
    pass
