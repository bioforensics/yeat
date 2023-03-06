# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pathlib import Path
from pkg_resources import resource_filename
from snakemake import snakemake


def run_pacbio(fastq, assembly_configs, outdir=".", cores=1, sample="sample", dryrun="dry"):
    snakefile = resource_filename("yeat", "workflows/snakefiles/Pacbio")
    fastq = Path(fastq).resolve()
    if not fastq.is_file():
        raise FileNotFoundError(f"No such file: '{fastq}'")
    # assemblers = [config.algorithm for config in assembly_configs]
    assemblers = ["flye"]
    extra_args = {config.algorithm: config.extra_args for config in assembly_configs}
    config = dict(fastq=fastq, assemblers=assemblers, extra_args=extra_args, sample=sample)
    success = snakemake(
        snakefile, config=config, cores=cores, dryrun=dryrun, printshellcmds=True, workdir=outdir
    )
    if not success:
        raise RuntimeError("Snakemake Failed")
