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
        read="analysis/{sample}/qc/hifi/downsample/read.fastq.gz"
    output:
        contigs="analysis/{sample}/yeat/unicycler/{label}/contigs.fasta"
    threads: 128
    params:
        outdir="analysis/{sample}/yeat/unicycler/{label}",
        extra_args=lambda wildcards: config["config"].assemblies[wildcards.label].extra_args
    shell:
        """
        unicycler -l {input.reads} -t {threads} -o {params.outdir} {params.extra_args}
        ln -s assembly.fasta {output.contigs}
        """


rule flye:
    input:
        read="analysis/{sample}/qc/hifi/downsample/read.fastq.gz"
    output:
        contigs="analysis/{sample}/yeat/flye/{label}/contigs.fasta"
    threads: 128
    params:
        outdir="analysis/{sample}/{readtype}/{label}/flye",
        extra_args=lambda wildcards: config["assemblies"][wildcards.label].extra_args
    shell:
        """
        flye --pacbio-hifi {input.reads} -t {threads} -o {params.outdir} {params.extra_args}
        ln -s assembly.fasta {output.contigs}
        """


rule canu:
    input:
        read="analysis/{sample}/qc/hifi/downsample/read.fastq.gz"
    output:
        contigs="analysis/{sample}/yeat/canu/{label}/contigs.fasta"
    threads: 128
    params:
        outdir="analysis/{sample}/{readtype}/{label}/canu",
        extra_args=lambda wildcards: config["assemblies"][wildcards.label].extra_args
    shell:
        """
        canu -pacbio-hifi {input.reads} maxThreads={threads} -p {wildcards.sample} -d {params.outdir} {params.extra_args} useGrid=false
        ln -s {wildcards.sample}.contigs.fasta {output.contigs}
        """


rule hifiasm:
    input:
        read="analysis/{sample}/qc/hifi/downsample/read.fastq.gz"
    output:
        contigs="analysis/{sample}/hifi/{label}/hifiasm/contigs.fasta"
    threads: 128
    params:
        prefix="analysis/{sample}/hifi/{label}/hifiasm/{sample}",
        extra_args=lambda wildcards: config["assemblies"][wildcards.label].extra_args
    shell:
        """
        hifiasm -o {params.prefix} -t {threads} {params.extra_args} {input.reads}
        gfatools gfa2fa {params.prefix}.bp.p_ctg.gfa > {params.prefix}.bp.p_ctg.fa
        ln -s {wildcards.sample}.bp.p_ctg.fa {output.contigs}
        """


rule hifiasm_meta:
    input:
        read="analysis/{sample}/qc/hifi/downsample/read.fastq.gz"
    output:
        contigs="analysis/{sample}/hifi/{label}/hifiasm_meta/contigs.fasta"
    threads: 128
    params:
        prefix="analysis/{sample}/hifi/{label}/hifiasm_meta/{sample}",
        extra_args=lambda wildcards: config["assemblies"][wildcards.label].extra_args
    shell:
        """
        hifiasm_meta -o {params.prefix} -t {threads} {params.extra_args} {input.reads}
        gfatools gfa2fa {params.prefix}.p_ctg.gfa > {params.prefix}.p_ctg.fa
        ln -s {wildcards.sample}.p_ctg.fa {output.contigs}
        """


rule metamdbg:
    input:
        read="analysis/{sample}/hifi/downsample/read.fastq.gz"
    output:
        contigs="analysis/{sample}/hifi/{label}/metamdbg/contigs.fasta"
    threads: 128
    params:
        outdir="analysis/{sample}/hifi/{label}/metamdbg",
        extra_args=lambda wildcards: config["assemblies"][wildcards.label].extra_args
    shell:
        """
        metaMDBG asm --out-dir {params.outdir} --in-hifi {input.reads} -t {threads} {params.extra_args}
        gunzip {params.outdir}/contigs.fasta.gz
        """
