# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

rule spades:
    input:
        r1="analysis/{sample}/qc/illumina_paired/downsample/R1.fastq.gz",
        r2="analysis/{sample}/qc/illumina_paired/downsample/R2.fastq.gz"
    output:
        contigs="analysis/{sample}/yeat/spades/{label}/contigs.fasta"
    threads: 128
    params:
        outdir="analysis/{sample}/yeat/spades/{label}",
        extra_args=lambda wildcards: config["config"].assemblies[wildcards.label].extra_args
    log:
        "analysis/{sample}/yeat/spades/{label}/spades-stdout-err.log"
    shell:
        """
        spades.py -1 {input.r1} -2 {input.r2} -t {threads} -o {params.outdir} {params.extra_args} > {log} 2>&1
        """


rule megahit:
    input:
        r1="analysis/{sample}/qc/illumina_paired/downsample/R1.fastq.gz",
        r2="analysis/{sample}/qc/illumina_paired/downsample/R2.fastq.gz"
    output:
        contigs="analysis/{sample}/yeat/megahit/{label}/contigs.fasta"
    threads: 128
    params:
        temp_dir="analysis/{sample}/yeat/megahit-temp/{label}",
        actual_dir="analysis/{sample}/yeat/megahit/{label}",
        extra_args=lambda wildcards: config["config"].assemblies[wildcards.label].extra_args
    log:
        "analysis/{sample}/yeat/megahit/{label}/megahit.log"
    shell:
        """
        megahit -1 {input.r} -2 {input.r2} -t {threads} -o {params.temp_dir} {params.extra_args} > {log} 2>&1
        mv {params.temp_dir}/* {params.actual_dir}
        rm -r {params.temp_dir}
        ln -s final.contigs.fa {output.contigs}
        """


rule unicycler:
    input:
        r1="analysis/{sample}/qc/illumina_paired/downsample/R1.fastq.gz",
        r2="analysis/{sample}/qc/illumina_paired/downsample/R2.fastq.gz"
    output:
        contigs="analysis/{sample}/yeat/unicyler/{label}/contigs.fasta"
    threads: 128
    params:
        outdir="analysis/{sample}/yeat/unicylcer/{label}",
        extra_args=lambda wildcards: config["config"].assemblies[wildcards.label].extra_args
    shell:
        """
        unicycler -1 {input.r1} -2 {input.r2} -t {threads} -o {params.outdir} {params.extra_args}
        ln -s assembly.fasta {output.contigs}
        """


rule penguin:
    input:
        r1="analysis/{sample}/qc/illumina_paired/downsample/R1.fastq.gz",
        r2="analysis/{sample}/qc/illumina_paired/downsample/R2.fastq.gz"
    output:
        contigs="analysis/{sample}/yeat/penguin/{label}/contigs.fasta"
    threads: 128
    params:
        outdir="analysis/{sample}/yeat/penguin/{label}",
        extra_args=lambda wildcards: config["config"].assemblies[wildcards.label].extra_args
    shell:
        """
        penguin guided_nuclassemble {input.r1} {input.r2} {params.outdir}/unpolished_contigs.fasta {params.outdir} --threads {threads} {params.extra_args}
        bowtie2-build {params.outdir}/unpolished_contigs.fasta {params.outdir}/unpolished_contigs.fasta
        bowtie2 -p {threads} -x {params.outdir}/unpolished_contigs.fasta -1 {input.read1} -2 {input.read2} 2> {params.outdir}/unpolished_contigs.bowtie.log | samtools view -b -@ {threads} | samtools sort -@ {threads} -o {params.outdir}/unpolished_contigs.sorted.bam
        samtools index {params.outdir}/unpolished_contigs.sorted.bam
        pilon --genome {params.outdir}/unpolished_contigs.fasta --bam {params.outdir}/unpolished_contigs.sorted.bam --output {params.outdir}/contigs
        """


rule velvet:
    input:
        r1="analysis/{sample}/qc/illumina_paired/downsample/R1.fastq.gz",
        r2="analysis/{sample}/qc/illumina_paired/downsample/R2.fastq.gz"
    output:
        contigs="analysis/{sample}/yeat/velvet/{label}/contigs.fasta"
    conda:
        "yeat-velvet"
    threads: 128
    params:
        temp_dir="analysis/{sample}/yeat/velvet-temp/{label}",
        actual_dir="analysis/{sample}/yeat/velvet/{label}",
        extra_args=lambda wildcards: config["config"].assemblies[wildcards.label].extra_args,
        reads=lambda wildcards, input: f"'-fastq.gz -shortPaired {input.r1} -shortPaired2 {input.r2}'",
    shell:
        """
        VelvetOptimiser.pl -f {params.reads} -t {threads} -p {params.actual_dir}/auto -d {params.temp_dir} {params.extra_args}
        mv {params.temp_dir}/* {params.actual_dir}
        rm -r {params.temp_dir}
        ln -s contigs.fa {output.contigs}
        """
