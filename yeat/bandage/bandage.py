# -------------------------------------------------------------------------------------------------
# Copyright (c) 2022, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pathlib import Path
import platform
from pkg_resources import resource_filename
from snakemake import snakemake
import warnings


bandage = {
    "Linux": Path("~/Bandage/Bandage").expanduser(),
    "macOS": Path("~/Bandage/Bandage.app/Contents/MacOS/Bandage").expanduser(),
}


def check_bandage_compatability(os):
    compatable = ["Linux", "macOS"]
    os = platform.platform().strip().split("-")[0]
    if os not in compatable:
        warnings.warn(f"yeat cannot support Bandage on this operating system: {os}")
        return False
    if os == "Linux" and not bandage["Linux"].exists():
        warnings.warn("Bandage does not exist!")
        return False
    elif os == "macOS" and not bandage["macOS"].exists():
        warnings.warn("Bandage does not exist!")
        return False
    return True


def run_bandage(assembly_configs, outdir=".", cores=1):
    os = platform.platform().strip().split("-")[0]
    if not check_bandage_compatability(os):
        return
    config = dict(
        bandage=bandage[os],
        assemblers=[config.algorithm for config in assembly_configs],
    )
    snakefile = resource_filename("yeat", "bandage/Snakefile")
    success = snakemake(
        snakefile,
        config=config,
        cores=cores,
        printshellcmds=True,
        workdir=outdir,
    )
    if not success:
        raise RuntimeError("Snakemake Failed")
