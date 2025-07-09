# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

rule spades:
    input:
        read="analysis/{sample}/qc/illumina_single/downsample/read.fastq.gz"
    output:
        contigs="analysis/{sample}/yeat/spades/{label}/contigs.fasta"
    threads: 128
    params:
        outdir="analysis/{sample}/yeat/spades/{label}",
        extra_args=lambda wildcards: config["config"].assemblies[wildcards.label].extra_args
    shell:
        """
        spades.py -s {input.read} -t {threads} -o {params.outdir} {params.extra_args}
        """


rule megahit:
    input:
        read="analysis/{sample}/qc/illumina_single/downsample/read.fastq.gz"
    output:
        contigs="analysis/{sample}/yeat/megahit/{label}/contigs.fasta"
    threads: 128
    params:
        temp_dir="analysis/{sample}/yeat/megahit-temp/{label}",
        actual_dir="analysis/{sample}/yeat/megahit/{label}",
        extra_args=lambda wildcards: config["config"].assemblies[wildcards.label].extra_args
    shell:
        """
        megahit -r {input.read} -t {threads} -o {params.temp_dir} {params.extra_args}
        mv {params.temp_dir}/* {params.actual_dir}
        rm -r {params.temp_dir}
        ln -s final.contigs.fa {output.contigs}
        """


rule unicycler:
    input:
        read="analysis/{sample}/qc/illumina_single/downsample/read.fastq.gz"
    output:
        contigs="analysis/{sample}/yeat/unicycler/{label}/contigs.fasta"
    threads: 128
    params:
        outdir="analysis/{sample}/single/{label}/unicycler",
        extra_args=lambda wildcards: config["assemblies"][wildcards.label].extra_args
    shell:
        """
        unicycler -s {input.read} -t {threads} -o {params.outdir} {params.extra_args}
        ln -s assembly.fasta {output.contigs}
        """


rule penguin:
    input:
        read="analysis/{sample}/qc/illumina_single/downsample/read.fastq.gz"
    output:
        contigs="analysis/{sample}/yeat/penguin/{label}/contigs.fasta"
    threads: 128
    params:
        outdir="analysis/{sample}/yeat/penguin/{label}",
        extra_args=lambda wildcards: config["assemblies"][wildcards.label].extra_args
    shell:
        """
        penguin guided_nuclassemble {input.read} {params.outdir}/unpolished_contigs.fasta {params.outdir} --threads {threads} {params.extra_args}
        bowtie2-build {params.outdir}/unpolished_contigs.fasta {params.outdir}/unpolished_contigs.fasta
        bowtie2 -p {threads} -x {params.outdir}/unpolished_contigs.fasta -U {input.read} 2> {params.outdir}/unpolished_contigs.bowtie.log | samtools view -b -@ {threads} | samtools sort -@ {threads} -o {params.outdir}/unpolished_contigs.sorted.bam
        samtools index {params.outdir}/unpolished_contigs.sorted.bam
        pilon --genome {params.outdir}/unpolished_contigs.fasta --bam {params.outdir}/unpolished_contigs.sorted.bam --output {params.outdir}/contigs
        """


rule velvet:
    input:
        read="analysis/{sample}/qc/illumina_single/downsample/read.fastq.gz"
    output:
        contigs="analysis/{sample}/yeat/velvet/{label}/contigs.fasta"
    conda:
        "yeat-velvet"
    threads: 128
    params:
        temp_dir="analysis/{sample}/yeat/velvet-temp/single/{label}",
        actual_dir="analysis/{sample}/yeat/velvet/{label}",
        extra_args=lambda wildcards: config["assemblies"][wildcards.label].extra_args,
        reads=lambda wildcards, input: f"'-fastq.gz {input.reads}'",
    shell:
        """
        VelvetOptimiser.pl -f {params.reads} -t {threads} -p {params.actual_dir}/auto -d {params.temp_dir} {params.extra_args}
        mv {params.temp_dir}/* {params.actual_dir}
        rm -r {params.temp_dir}
        ln -s contigs.fa {output.contigs}
        """
