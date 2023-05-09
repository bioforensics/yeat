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
    files_by_samplename,
    assembly_configs,
    outdir=".",
    cores=1,
    dryrun="dry",
    coverage=150,
    downsample=0,
    genomesize=0,
    seed=None,
):
    snakefile = resource_filename("yeat", "workflows/snakefiles/Paired")
    labels = [config.label for config in assembly_configs]
    assemblers = {config.label: config.algorithm for config in assembly_configs}
    extra_args = {config.label: config.extra_args for config in assembly_configs}
    config = dict(
        data=files_by_samplename,
        labels=labels,
        assemblers=assemblers,
        extra_args=extra_args,
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


def run_pacbio(
    files_by_samplename, assembly_configs, outdir=".", cores=1, dryrun="dry"
):
    snakefile = resource_filename("yeat", "workflows/snakefiles/Pacbio")
    fastq = Path(fastq).resolve()
    if not fastq.is_file():
        raise FileNotFoundError(f"No such file: '{fastq}'")
    assemblers = [config.algorithm for config in assembly_configs]
    extra_args = {config.algorithm: config.extra_args for config in assembly_configs}
    if "canu" in assemblers:
        check_canu_required_params(extra_args["canu"], cores)
    config = dict(
        fastq=fastq, assemblers=assemblers, extra_args=extra_args, threads=cores
    )
    success = snakemake(
        snakefile, config=config, cores=cores, dryrun=dryrun, printshellcmds=True, workdir=outdir
    )
    if not success:
        raise RuntimeError("Snakemake Failed")


def run_workflow(args, files_by_samplename, assembly_configs):
    if args.paired:
        run_paired(
            files_by_samplename,
            assembly_configs=assembly_configs,
            outdir=args.outdir,
            cores=args.threads,
            dryrun=args.dry_run,
            coverage=args.coverage,
            downsample=args.downsample,
            genomesize=args.genome_size,
            seed=args.seed,
        )
    # elif args.pacbio:
    #     run_pacbio(
    #         files_by_samplename,
    #         assembly_configs=assembly_configs,
    #         outdir=args.outdir,
    #         cores=args.threads,
    #         dryrun=args.dry_run,
    #         # coverage=args.coverage,
    #         # downsample=args.downsample,
    #         # genomesize=args.genome_size,
    #         # seed=args.seed,
    #     )
