# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from collections import defaultdict
import json
from pathlib import Path


EXTENSIONS = (".fastq", ".fastq.gz", ".fq", ".fq.gz")


class AutoPopError(ValueError):
    pass


class AutoPop:
    def __init__(self, args):
        self.samples = self.get_samples(args.samples)
        self.check_samples()
        self.files = self.get_files(args.files, args.seq_path)
        self.files_to_samples = self.organize_files_to_samples()
        self.check_files_to_samples()
        self.write_config_file(args.outfile)

    def get_samples(self, samples):
        if len(samples) == 1 and Path(samples[0]).is_file():
            with open(samples[0], "r") as fh:
                samples = fh.read().strip().split("\n")
        return list(sorted(samples))

    def check_samples(self):
        for s1_index, s1 in enumerate(self.samples):
            for s2_index, s2 in enumerate(self.samples):
                if s1 == s2 and s1_index == s2_index:
                    continue
                if s1 in s2:
                    message = f"cannot correctly process a sample name that is a substring of another sample name: {s1} vs. {s2}"
                    raise ValueError(message)

    def get_files(self, files, seq_path):
        if files:
            return files
        files = []
        for file in self.traverse(seq_path):
            if not file.name.endswith(EXTENSIONS):
                continue
            files.append(file)
        return files

    def traverse(self, dirpath):
        dirpath = Path(dirpath)
        if not dirpath.is_dir():
            return
        for subpath in dirpath.iterdir():
            if subpath.is_dir():
                yield from self.traverse(subpath)
            else:
                yield subpath

    def organize_files_to_samples(self):
        files_to_samples = defaultdict(list)
        for sample in self.samples:
            files_to_samples[sample] = [
                str(file.absolute()) for file in self.files if sample in str(file)
            ]
        return files_to_samples

    def check_files_to_samples(self):
        for sample, files in self.files_to_samples.items():
            if len(files) != 2:
                message = f"sample {sample}: expected 2 FASTQ files for paired-end data, found {len(files)}"
                raise AutoPopError(message)

    def write_config_file(self, outfile):
        samples = {}
        for label, reads in self.files_to_samples.items():
            samples[label] = {"paired": [reads]}
        data = {"samples": samples, "assemblies": {}}
        outdir = Path(outfile).parent.absolute()
        outdir.mkdir(parents=True, exist_ok=True)
        outfile = open(outfile, "w")
        json.dump(data, outfile, indent=4)
