# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from importlib.resources import files
from pathlib import Path
from snakemake import snakemake
import toml


def run_workflow(args):
    snakefile = files("yeat") / "workflow" / "Snakefile.smk"
    config = vars(args)
    config["config"] = get_config_data(config["config"])
    # config["bandage"] = check_bandage()
    success = snakemake_local(args, snakefile, config)
    if not success:
        raise RuntimeError("Snakemake Failed")  # pragma: no cover


def get_config_data(infile):
    data = toml.load(open(infile))
    for sample_label, sample_data in data["samples"].items():
        for readtype, reads in sample_data.items():
            data["samples"][sample_label][readtype] = str(Path(reads).resolve())
    return data


# def check_bandage():
#     try:
#         completed_process = subprocess.run(["Bandage", "--help"], capture_output=True, text=True)
#     except Exception as exception:
#         print(f"{type(exception).__name__}: {exception}")
#         warnings.warn("Unable to run Bandage; skipping Bandage")
#         return False
#     if completed_process.returncode == 1:
#         print(completed_process.stderr)
#         warnings.warn("Unable to run Bandage; skipping Bandage")
#         return False
#     return True


def snakemake_local(args, snakefile, config):
    success = snakemake(
        snakefile,
        config=config,
        cores=args.threads,
        dryrun=args.dry_run,
        printshellcmds=True,
        workdir=args.workdir,
        use_conda=True,
    )
    return success
