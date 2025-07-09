# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

rule unicycler:
    input:
        read="analysis/{sample}/qc/{platform}/downsample/read.fastq.gz"
    output:
        contigs="analysis/{sample}/yeat/unicycler/{label}/contigs.fasta"
    threads: 128
    wildcard_constraints:
        platform="simplex|duplex|ultra_long"
    params:
        outdir="analysis/{sample}/yeat/unicycler/{label}",
        extra_args=lambda wildcards: config["config"].assemblies[wildcards.label].extra_args
    shell:
        """
        unicycler -l {input.read} -t {threads} -o {params.outdir} {params.extra_args}
        ln -s assembly.fasta {output.contigs}
        """


rule flye:
    input:
        read="analysis/{sample}/qc/{platform}/downsample/read.fastq.gz"
    output:
        contigs="analysis/{sample}/yeat/flye/{label}/contigs.fasta"
    threads: 128
    wildcard_constraints:
        platform="simplex|duplex|ultra_long"
    params:
        outdir="analysis/{sample}/yeat/flye/{label}",
        extra_args=lambda wildcards: config["config"].assemblies[wildcards.label].extra_args
    shell:
        """
        flye --nano-hq {input.read} -t {threads} -o {params.outdir} {params.extra_args}
        ln -s assembly.fasta {output.contigs}
        """


rule canu:
    input:
        read="analysis/{sample}/qc/{platform}/downsample/read.fastq.gz"
    output:
        contigs="analysis/{sample}/yeat/canu/{label}/contigs.fasta"
    threads: 128
    wildcard_constraints:
        platform="simplex|duplex|ultra_long"
    params:
        outdir="analysis/{sample}/yeat/canu/{label}",
        extra_args=lambda wildcards: config["config"].assemblies[wildcards.label].extra_args
    shell:
        """
        canu -nanopore {input.read} maxThreads={threads} -p {wildcards.sample} -d {params.outdir} {params.extra_args} useGrid=false
        ln -s {wildcards.sample}.contigs.fasta {output.contigs}
        """


rule metamdbg:
    input:
        read="analysis/{sample}/qc/{platform}/downsample/read.fastq.gz"
    output:
        contigs="analysis/{sample}/yeat/metamdbg/{label}/contigs.fasta"
    threads: 128
    wildcard_constraints:
        platform="simplex|duplex|ultra_long"
    params:
        outdir="analysis/{sample}/yeat/metamdbg/{label}",
        extra_args=lambda wildcards: config["config"].assemblies[wildcards.label].extra_args
    shell:
        """
        metaMDBG asm --out-dir {params.outdir} --in-ont {input.read} --threads {threads} {params.extra_args}
        gunzip {params.outdir}/contigs.fasta.gz
        """
    