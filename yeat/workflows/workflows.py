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


def run_paired(
    fastq1,
    fastq2,
    assembly_configs,
    outdir=".",
    cores=1,
    sample="sample",
    dryrun="dry",
    downsample=0,
    coverage=150,
    seed=None,
    genomesize=0,
):
    snakefile = resource_filename("yeat", "workflows/snakefiles/Paired")
    r1 = Path(fastq1).resolve()
    if not r1.is_file():
        raise FileNotFoundError(f"No such file: '{r1}'")
    r2 = Path(fastq2).resolve()
    if not r2.is_file():
        raise FileNotFoundError(f"No such file: '{r2}'")
    assemblers = [config.algorithm for config in assembly_configs]
    extra_args = {config.algorithm: config.extra_args for config in assembly_configs}
    config = dict(
        read1=r1,
        read2=r2,
        assemblers=assemblers,
        extra_args=extra_args,
        sample=sample,
        threads=cores,
        downsample=downsample,
        coverage=coverage,
        seed=seed,
        genomesize=genomesize,
    )
    success = snakemake(
        snakefile, config=config, cores=cores, dryrun=dryrun, printshellcmds=True, workdir=outdir
    )
    if not success:
        raise RuntimeError("Snakemake Failed")


def check_canu_required_params(extra_args, cores):
    if "genomeSize=" not in extra_args:
        raise ValueError("Missing required input argument from config: 'genomeSize'")
    if cores < 4:
        raise ValueError(
            "Canu requires at least 4 avaliable cores; increase `--threads` to 4 or more"
        )


def run_pacbio(fastq, assembly_configs, outdir=".", cores=1, sample="sample", dryrun="dry"):
    snakefile = resource_filename("yeat", "workflows/snakefiles/Pacbio")
    fastq = Path(fastq).resolve()
    if not fastq.is_file():
        raise FileNotFoundError(f"No such file: '{fastq}'")
    assemblers = [config.algorithm for config in assembly_configs]
    extra_args = {config.algorithm: config.extra_args for config in assembly_configs}
    if "canu" in assemblers:
        check_canu_required_params(extra_args["canu"], cores)
    config = dict(
        fastq=fastq, assemblers=assemblers, extra_args=extra_args, sample=sample, threads=cores
    )
    success = snakemake(
        snakefile, config=config, cores=cores, dryrun=dryrun, printshellcmds=True, workdir=outdir
    )
    if not success:
        raise RuntimeError("Snakemake Failed")


def run_workflow(args, assembly_configs):
    if args.paired is not None:
        run_paired(
            *args.paired,
            assembly_configs=assembly_configs,
            outdir=args.outdir,
            cores=args.threads,
            sample=args.sample,
            dryrun=args.dry_run,
            downsample=args.downsample,
            coverage=args.coverage,
            seed=args.seed,
            genomesize=args.genome_size,
        )
    elif args.pacbio is not None:
        run_pacbio(
            args.pacbio,
            assembly_configs=assembly_configs,
            outdir=args.outdir,
            cores=args.threads,
            sample=args.sample,
            dryrun=args.dry_run,
        )
