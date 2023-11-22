# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from glob import glob
import re
import shutil
import subprocess
import warnings


def get_and_filter_contig_files(sample, readtype, label):
    pattern = rf"analysis/{sample}/{readtype}/{label}/megahit/intermediate_contigs/k\d+.contigs.fa"
    contigs = glob(rf"analysis/{sample}/{readtype}/{label}/megahit/intermediate_contigs/k*.contigs.fa")
    return filter(re.compile(pattern).match, contigs)


def get_canu_readtype_flag(readtype):
    if readtype in ["pacbio-raw", "pacbio-corr"]:
        return "-pacbio"
    elif readtype == "pacbio-hifi":
        return "-pacbio-hifi"


def combine(reads, direction, outdir):
    for i, inread in enumerate(reads):
        outread = f"{outdir}/{direction}_reads{i}.fq"
        if inread.endswith(".gz"):
            subprocess.run(f"gunzip -c {inread} > {outread}", shell=True)
        else:
            shutil.copyfile(inread, outread)
    subprocess.run(f"cat {outdir}/{direction}_reads*.fq > {outdir}/{direction}_combined-reads.fq", shell=True)
    subprocess.run(f"gzip {outdir}/{direction}_combined-reads.fq", shell=True)


def get_expected_files(config):
    run_bandage = check_bandage()
    inputlist = []
    for assembly_label, assembly_obj in config["assemblies"].items():
        for sample_label in assembly_obj.samples:
            sample_obj = config["samples"][sample_label]
            if assembly_obj.mode in ["paired", "single"]:
                inputlist.append(get_file(sample_label, sample_obj.short_readtype, assembly_label, assembly_obj.algorithm, run_bandage))
            elif assembly_obj.mode in ["pacbio", "oxford"]:
                inputlist.append(get_file(sample_label, sample_obj.long_readtype, assembly_label, assembly_obj.algorithm, run_bandage))
            if assembly_obj.mode == "paired":
                inputlist += [f"seq/fastqc/{sample_label}/paired/{direction}_combined-reads_fastqc.html" for direction in ["r1", "r2"]]
            elif assembly_obj.mode == "oxford":
                inputlist += [f"seq/nanoplot/{sample_label}/{sample_obj.long_readtype}/{quality}_LengthvsQualityScatterPlot_dot.pdf" for quality in ["raw", "filtered"]]
            else:
                inputlist.append(f"seq/fastqc/{sample_label}/single/combined-reads_fastqc.html")
    return inputlist


def check_bandage():
    try:
        completed_process = subprocess.run(["Bandage", "--help"], capture_output=True, text=True)
    except Exception as exception:
        print(f"{type(exception).__name__}: {exception}")
        warnings.warn("Unable to run Bandage; skipping Bandage")
        return False
    if completed_process.returncode == 1:
        print(completed_process.stderr)
        warnings.warn("Unable to run Bandage; skipping Bandage")
        print("here")
        return False
    return True


def get_file(sample, readtype, assembly, algorithm, run_bandage):
    if run_bandage:
        return f"analysis/{sample}/{readtype}/{assembly}/{algorithm}/bandage/.done"
    else:
        return f"analysis/{sample}/{readtype}/{assembly}/{algorithm}/quast/report.html"
