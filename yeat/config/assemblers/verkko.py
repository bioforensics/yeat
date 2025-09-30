# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .assembler import Assembler
from glob import glob


class VerkkoAssembler(Assembler):
    @staticmethod
    def _check_sample_compatibility(sample):
        return sample.has_long_reads

    @property
    def targets(self):
        targets = list()
        for sample in self.samples.values():
            label_dir = f"analysis/{sample.label}/yeat/verkko/{self.label}"
            targets.append(f"{label_dir}/quast/report.html")
            targets.append(f"{label_dir}/bandage/.done")
        return targets

    def input_files(self, sample):
        infiles = dict()
        for read_type in ["pacbio_hifi", "ont_duplex", "ont_ultralong"]:
            if read_type in self.samples[sample].data:
                infiles[read_type] = [f"analysis/{sample}/qc/{read_type}/downsample/read.fastq.gz"]
        return infiles

    def input_args(self, sample):
        reads = self.input_files(sample)
        args = []
        args.extend(self.get_long_args(reads))
        return " ".join(args)

    def get_long_args(self, reads):
        args = ["--hifi"]
        for read_type in ["pacbio_hifi", "ont_duplex"]:
            if read_type in reads:
                args.append(reads[read_type][0])
        if len(args) == 1:
            # print("ultralong for --nano")
            assert 0
        if "ont_ultralong" in reads:
            args.extend(["--nano", reads["ont_ultralong"][0]])
        return args

    def gfa_files(self, sample):
        return glob(f"analysis/{sample}/yeat/verkko/{self.label}/*.gfa")
