# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pkg_resources import resource_filename
from snakemake import snakemake
import subprocess
import warnings


def check_bandage():
    try:
        completed_process = subprocess.run(["Bandage", "--help"], capture_output=True, text=True)
    except Exception as exception:
        print(f"{type(exception).__name__}: {exception}")
        return False
    if completed_process.returncode == 1:
        print(completed_process.stderr)
        return False
    return True


def run_bandage(assembly_configs, outdir=".", cores=1):
    if not check_bandage():
        warnings.warn("Unable to run Bandage; skipping Bandage")
        return
    labels = [config.label for config in assembly_configs]
    assemblers = {config.label: config.algorithm for config in assembly_configs}
    label_to_samples = {config.label: config.samples for config in assembly_configs}
    config = dict(
        labels=labels,
        assemblers=assemblers,
        label_to_samples=label_to_samples,
    )
    snakefile = resource_filename("yeat", "workflows/snakefiles/Bandage")
    success = snakemake(snakefile, config=config, cores=cores, printshellcmds=True, workdir=outdir)
    if not success:
        raise RuntimeError("Snakemake Failed")