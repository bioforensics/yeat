# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pathlib import Path
from typing import List
from warnings import warn


def traverse(dirpath):
    dirpath = Path(dirpath)
    if not dirpath.is_dir():
        return
    for subpath in dirpath.iterdir():
        if subpath.is_dir():
            yield from traverse(subpath)
        else:
            yield subpath


def get_fastq_files(files):
    file_paths = [Path(file).resolve() for file in files] if len(files) > 1 else traverse(files[0])
    suffixes = (".fastq", ".fastq.gz", ".fq", ".fq.gz")
    fastq_files = []
    for file_path in file_paths:
        if not file_path.is_file():
            raise FileNotFoundError(f"No such file: '{r1}'")
        if not file_path.name.endswith(suffixes):
            continue
        fastq_files.append(file_path)
    return fastq_files


def get_sample_names(samplenames):
    if len(samplenames) > 1 or not samplenames[0].endswith(".txt"):
        return samplenames
    with open(Path(samplenames[0]), "r") as fh:
        sample_names = fh.read().strip().split("\n")
    return sample_names


def remove_dupes_and_check_sample_names(sample_names):
    A = set(sample_names)
    if len(sample_names) > len(A):
        warn(f"Removed {len(sample_names)-len(A)} duplicate sample name(s)")
    for s1 in A:
        for s2 in A:
            if s1 == s2:
                continue
            if s1 in s2:
                message = f"cannot correctly process a sample name that is a substring of another sample name: {s1} vs. {s2}"
                raise ValueError(message)
    return A


def get_files_by_samplename(files: List[str], samplenames: List[str]):
    fastq_files = get_fastq_files(files)
    sample_names = get_sample_names(samplenames)
    sample_names = remove_dupes_and_check_sample_names(sample_names)
    files_by_samplename = dict()
    for samplename in sample_names:
        matching = [s for s in fastq_files if s.name.startswith(samplename)]
        files_by_samplename[samplename] = matching
    return files_by_samplename
