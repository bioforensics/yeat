# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from . import bandage
from pathlib import Path
from pkg_resources import resource_filename
from snakemake import snakemake


PAIRED = ["spades", "megahit", "unicycler"]
PACBIO = ["canu", "flye"]


def run_paired(
    assembly_samples,
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
    samples = {k: v.sample for k, v in assembly_samples.items()}
    labels = [config.label for config in assembly_configs]
    assemblers = {config.label: config.algorithm for config in assembly_configs}
    extra_args = {config.label: config.extra_args for config in assembly_configs}
    label_to_samples = {config.label: config.samples for config in assembly_configs}
    config = dict(
        samples=samples,
        labels=labels,
        assemblers=assemblers,
        extra_args=extra_args,
        label_to_samples=label_to_samples,
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


def run_pacbio(assembly_samples, assembly_configs, outdir=".", cores=1, dryrun="dry"):
    snakefile = resource_filename("yeat", "workflows/snakefiles/Pacbio")
    samples = {k: v.sample for k, v in assembly_samples.items()}
    labels = [config.label for config in assembly_configs]
    assemblers = {config.label: config.algorithm for config in assembly_configs}
    extra_args = {config.label: config.extra_args for config in assembly_configs}
    label_to_samples = {config.label: config.samples for config in assembly_configs}
    if "canu" in assemblers:
        check_canu_required_params(extra_args["canu"], cores)
    config = dict(
        samples=samples,
        labels=labels,
        assemblers=assemblers,
        extra_args=extra_args,
        label_to_samples=label_to_samples,
        threads=cores,
    )
    success = snakemake(
        snakefile, config=config, cores=cores, dryrun=dryrun, printshellcmds=True, workdir=outdir
    )
    if not success:
        raise RuntimeError("Snakemake Failed")


def get_assembly_samples(samples, config):
    assembly_samples = {}
    for assembly in config:
        assembly_samples = assembly_samples | dict(
            (k, samples[k]) for k in assembly.samples if k in samples
        )
    return assembly_samples


def run_workflows(args, samples, assembly_configs):
    paired_configs = []
    pacbio_configs = []
    for assembly in assembly_configs:
        if assembly.algorithm in PAIRED:
            paired_configs.append(assembly)
        elif assembly.algorithm in PACBIO:
            pacbio_configs.append(assembly)
    if paired_configs:
        assembly_samples = get_assembly_samples(samples, paired_configs)
        run_paired(
            assembly_samples,
            paired_configs,
            outdir=args.outdir,
            cores=args.threads,
            dryrun=args.dry_run,
            coverage=args.coverage,
            downsample=args.downsample,
            genomesize=args.genome_size,
            seed=args.seed,
        )
    elif pacbio_configs:
        assembly_samples = get_assembly_samples(samples, pacbio_configs)
        run_pacbio(
            assembly_samples,
            pacbio_configs,
            outdir=args.outdir,
            cores=args.threads,
            dryrun=args.dry_run,
            # coverage=args.coverage,
            # downsample=args.downsample,
            # genomesize=args.genome_size,
            # seed=args.seed,
        )
    if not args.dry_run:
        bandage.run_bandage(
            samples, assembly_configs=assembly_configs, outdir=args.outdir, cores=args.threads
        )
