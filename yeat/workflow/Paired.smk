# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

rule spades:
    output:
        contigs="analysis/{sample}/yeat/spades/contigs.fasta"
    input:
        r1="analysis/{sample}/qc/illumina/downsample/R1.fastq.gz",
        r2="analysis/{sample}/qc/illumina/downsample/R2.fastq.gz"
    threads: 128
    params:
        outdir="analysis/{sample}/yeat/spades",
        # extra_args=lambda wildcards: config["assemblies"][wildcards.label].extra_args
        extra_args=""
    log:
        "analysis/{sample}/yeat/spades/spades-stdout-err.log"
    shell:
        """
        spades.py -1 {input.r1} -2 {input.r2} -t {threads} -o {params.outdir} {params.extra_args} > {log} 2>&1
        """


rule megahit:
    output:
        contigs="analysis/{sample}/paired/{label}/megahit/contigs.fasta"
    input:
        read1="seq/downsample/{sample}/paired/{sample}.R1.fq.gz",
        read2="seq/downsample/{sample}/paired/{sample}.R2.fq.gz"
    threads: 128
    params:
        temp_dir="analysis/{sample}/paired/{label}/megahit-temp",
        actual_dir="analysis/{sample}/paired/{label}/megahit",
        extra_args=lambda wildcards: config["assemblies"][wildcards.label].extra_args
    log:
        "analysis/{sample}/paired/{label}/megahit/megahit.log"
    shell:
        """
        megahit -1 {input.read1} -2 {input.read2} -t {threads} -o {params.temp_dir} {params.extra_args} > {log} 2>&1
        mv {params.temp_dir}/* {params.actual_dir}
        rm -r {params.temp_dir}
        ln -s final.contigs.fa {output.contigs}
        """


rule unicycler:
    output:
        contigs="analysis/{sample}/paired/{label}/unicycler/contigs.fasta"
    input:
        read1="seq/downsample/{sample}/paired/{sample}.R1.fq.gz",
        read2="seq/downsample/{sample}/paired/{sample}.R2.fq.gz"
    threads: 128
    params:
        outdir="analysis/{sample}/paired/{label}/unicycler",
        extra_args=lambda wildcards: config["assemblies"][wildcards.label].extra_args
    shell:
        """
        unicycler -1 {input.read1} -2 {input.read2} -t {threads} -o {params.outdir} {params.extra_args}
        ln -s assembly.fasta {output.contigs}
        """


rule penguin:
    output:
        contigs="analysis/{sample}/paired/{label}/penguin/contigs.fasta"
    input:
        read1="seq/downsample/{sample}/paired/{sample}.R1.fq.gz",
        read2="seq/downsample/{sample}/paired/{sample}.R2.fq.gz"
    threads: 128
    params:
        outdir="analysis/{sample}/paired/{label}/penguin",
        extra_args=lambda wildcards: config["assemblies"][wildcards.label].extra_args
    shell:
        """
        penguin guided_nuclassemble {input.read1} {input.read2} {params.outdir}/unpolished_contigs.fasta {params.outdir} --threads {threads} {params.extra_args}
        bowtie2-build {params.outdir}/unpolished_contigs.fasta {params.outdir}/unpolished_contigs.fasta
        bowtie2 -p {threads} -x {params.outdir}/unpolished_contigs.fasta -1 {input.read1} -2 {input.read2} 2> {params.outdir}/unpolished_contigs.bowtie.log | samtools view -b -@ {threads} | samtools sort -@ {threads} -o {params.outdir}/unpolished_contigs.sorted.bam
        samtools index {params.outdir}/unpolished_contigs.sorted.bam
        pilon --genome {params.outdir}/unpolished_contigs.fasta --bam {params.outdir}/unpolished_contigs.sorted.bam --output {params.outdir}/contigs
        """


rule velvet:
    output:
        contigs="analysis/{sample}/paired/{label}/velvet/contigs.fasta"
    input:
        read1="seq/downsample/{sample}/paired/{sample}.R1.fq.gz",
        read2="seq/downsample/{sample}/paired/{sample}.R2.fq.gz"
    conda:
        "yeat-velvet"
    threads: 128
    params:
        temp_dir="analysis/{sample}/paired/{label}/velvet-temp",
        actual_dir="analysis/{sample}/paired/{label}/velvet",
        extra_args=lambda wildcards: config["assemblies"][wildcards.label].extra_args,
        reads=lambda wildcards, input: f"'-fastq.gz -shortPaired {input.read1} -shortPaired2 {input.read2}'",
    shell:
        """
        VelvetOptimiser.pl -f {params.reads} -t {threads} -p {params.actual_dir}/auto -d {params.temp_dir} {params.extra_args}
        mv {params.temp_dir}/* {params.actual_dir}
        rm -r {params.temp_dir}
        ln -s contigs.fa {output.contigs}
        """
