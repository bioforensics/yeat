# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pathlib import Path
import sys
import toml


EXTENSIONS = (".fastq", ".fastq.gz", ".fq", ".fq.gz")


class AutoPopError(ValueError):
    pass


class AutoPop:
    def __init__(self, samples, seq_path, files):
        self.samples = self.get_samples(samples)
        self.check_samples()
        self.check_seq_path(seq_path)
        self.files = [Path(f) for f in files] if files is not None else self.get_files(seq_path)
        self.check_files()
        self.files_to_samples = self.organize_files_to_samples()

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
                    raise AutoPopError(message)

    def check_seq_path(self, seq_path):
        if not seq_path:
            return
        if not Path(seq_path).exists():
            raise FileNotFoundError(seq_path)

    def get_files(self, seq_path):
        files = []
        for file in self.traverse(seq_path):
            if not file.name.endswith(EXTENSIONS):
                continue
            files.append(file)
        files.sort()
        return files

    def traverse(self, dirpath):
        dirpath = Path(dirpath)
        if not dirpath.is_dir():
            return  # pragma: no cover
        for subpath in dirpath.iterdir():
            if subpath.is_dir():
                yield from self.traverse(subpath)
            else:
                yield subpath

    def check_files(self):
        for file in self.files:
            if not file.exists():
                raise FileNotFoundError(file)

    def organize_files_to_samples(self):
        files_to_samples = dict()
        for sample in self.samples:
            temp = [str(file) for file in self.files if sample in str(file)]
            if len(temp) != 2:
                message = f"sample {sample}: expected 2 FASTQ files for paired-end data, found {len(temp)}"
                raise AutoPopError(message)
            prefix, suffix = self.find_common_prefix_suffix(temp)
            files_to_samples[sample] = f"{prefix}*{suffix}"
        return files_to_samples

    def find_common_prefix_suffix(self, strings):
        prefix = strings[0]
        suffix = strings[0]
        for s in strings[1:]:
            i = 0
            while i < min(len(prefix), len(s)) and prefix[i] == s[i]:
                i += 1
            prefix = prefix[:i]
        for s in strings[1:]:
            i = 1
            while i <= min(len(suffix), len(s)) and suffix[-i] == s[-i]:
                i += 1
            suffix = suffix[-(i - 1) :] if i > 1 else ""
        return prefix, suffix

    def write_config_file(self):
        data = self.get_config_data()
        toml.dump(data, sys.stdout)

    def get_config_data(self):
        samples = {}
        for label, regex_path in self.files_to_samples.items():
            samples[label] = {"illumina": regex_path}
        assemblers = {"spades_default": {"algorithm": "spades"}}
        return {"samples": samples, "assemblers": assemblers}
