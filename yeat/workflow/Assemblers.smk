# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from pathlib import Path


rule spades:
    input:
        reads=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_files(wildcards.sample),
    output:
        contigs="analysis/{sample}/yeat/spades/{label}/contigs.fasta",
    threads: 128
    params:
        outdir="analysis/{sample}/yeat/spades/{label}",
        input_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_args(wildcards.sample),
        extra_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .extra_args,
    log:
        "analysis/{sample}/yeat/spades/{label}/spades.log",
    shell:
        """
        spades.py {params.input_args} -t {threads} -o {params.outdir} {params.extra_args} > {log} 2>&1
        """


rule megahit:
    input:
        reads=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_files(wildcards.sample),
    output:
        contigs="analysis/{sample}/yeat/megahit/{label}/contigs.fasta",
    threads: 128
    params:
        temp_outdir="analysis/{sample}/yeat/megahit/{label}/megahit-temp",
        outdir="analysis/{sample}/yeat/megahit/{label}",
        input_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_args(wildcards.sample),
        extra_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .extra_args,
    log:
        "analysis/{sample}/yeat/megahit/{label}/megahit.log",
    shell:
        """
        megahit {params.input_args} -t {threads} -o {params.temp_outdir} {params.extra_args} > {log} 2>&1
        mv {params.temp_outdir}/* {params.outdir}
        rm -r {params.temp_outdir}
        ln -s final.contigs.fa {output.contigs}
        """


rule unicycler:
    input:
        reads=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_files(wildcards.sample),
    output:
        contigs="analysis/{sample}/yeat/unicycler/{label}/contigs.fasta",
    threads: 128
    params:
        outdir="analysis/{sample}/yeat/unicycler/{label}",
        input_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_args(wildcards.sample),
        extra_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .extra_args,
    log:
        "analysis/{sample}/yeat/unicycler/{label}/unicycler.log",
    shell:
        """
        unicycler {params.input_args} -t {threads} -o {params.outdir} {params.extra_args} > {log} 2>&1
        ln -s assembly.fasta {output.contigs}
        """


rule penguin:
    input:
        reads=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_files(wildcards.sample),
    output:
        contigs="analysis/{sample}/yeat/penguin/{label}/contigs.fasta",
    threads: 128
    params:
        outdir="analysis/{sample}/yeat/penguin/{label}",
        input_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_args(wildcards.sample),
        extra_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .extra_args,
        bowtie2_input_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .bowtie2_input_args(wildcards.sample),
    log:
        "analysis/{sample}/yeat/penguin/{label}/penguin.log",
    shell:
        """
        penguin guided_nuclassemble {params.input_args} {params.outdir}/unpolished_contigs.fasta {params.outdir} --threads {threads} {params.extra_args} > {log} 2>&1
        bowtie2-build {params.outdir}/unpolished_contigs.fasta {params.outdir}/unpolished_contigs.fasta >> {log} 2>&1
        bowtie2 -p {threads} -x {params.outdir}/unpolished_contigs.fasta {params.bowtie2_input_args} 2> {params.outdir}/unpolished_contigs.bowtie.log | samtools view -b -@ {threads} | samtools sort -@ {threads} -o {params.outdir}/unpolished_contigs.sorted.bam
        samtools index {params.outdir}/unpolished_contigs.sorted.bam
        pilon --genome {params.outdir}/unpolished_contigs.fasta --bam {params.outdir}/unpolished_contigs.sorted.bam --output {params.outdir}/contigs >> {log} 2>&1
        """


rule velvet:
    input:
        reads=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_files(wildcards.sample),
    output:
        contigs="analysis/{sample}/yeat/velvet/{label}/contigs.fasta",
    conda:
        "yeat-velvet"
    threads: 128
    params:
        temp_outdir="analysis/{sample}/yeat/velvet/{label}/velvet-temp",
        outdir="analysis/{sample}/yeat/velvet/{label}",
        input_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_args(wildcards.sample),
        extra_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .extra_args,
    log:
        "analysis/{sample}/yeat/velvet/{label}/velvet.log",
    shell:
        """
        VelvetOptimiser.pl -f {params.input_args} -t {threads} -p {params.outdir}/auto -d {params.temp_outdir} {params.extra_args} > {log} 2>&1
        mv {params.temp_outdir}/* {params.outdir}
        rm -r {params.temp_outdir}
        ln -s contigs.fa {output.contigs}
        """


rule flye:
    input:
        reads=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_files(wildcards.sample),
    output:
        contigs="analysis/{sample}/yeat/flye/{label}/contigs.fasta",
    threads: 128
    params:
        outdir="analysis/{sample}/yeat/flye/{label}",
        input_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_args(wildcards.sample),
        extra_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .extra_args,
    shell:
        """
        flye {params.input_args} -t {threads} -o {params.outdir} {params.extra_args}
        ln -s assembly.fasta {output.contigs}
        """


rule canu:
    input:
        reads=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_files(wildcards.sample),
    output:
        contigs="analysis/{sample}/yeat/canu/{label}/contigs.fasta",
    threads: 128
    params:
        outdir="analysis/{sample}/yeat/canu/{label}",
        input_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_args(wildcards.sample),
        extra_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .extra_args,
    shell:
        """
        canu {params.input_args} maxThreads={threads} -p {wildcards.sample} -d {params.outdir} {params.extra_args} useGrid=false
        ln -s {wildcards.sample}.contigs.fasta {output.contigs}
        """


rule hifiasm:
    input:
        reads=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_files(wildcards.sample),
    output:
        contigs="analysis/{sample}/yeat/hifiasm/{label}/contigs.fasta",
    threads: 128
    params:
        prefix="analysis/{sample}/hifi/{label}/hifiasm/{sample}",
        input_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_args(wildcards.sample),
        extra_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .extra_args,
    shell:
        """
        hifiasm -o {params.prefix} -t {threads} {params.extra_args} {params.input_args}
        gfatools gfa2fa {params.prefix}.bp.p_ctg.gfa > {params.prefix}.bp.p_ctg.fa
        ln -s {wildcards.sample}.bp.p_ctg.fa {output.contigs}
        """


rule hifiasm_meta:
    input:
        reads=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_files(wildcards.sample),
    output:
        contigs="analysis/{sample}/yeat/hifiasm_meta/{label}/contigs.fasta",
    threads: 128
    params:
        prefix="analysis/{sample}/hifi/{label}/hifiasm_meta/{sample}",
        input_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_args(wildcards.sample),
        extra_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .extra_args,
    shell:
        """
        hifiasm_meta -o {params.prefix} -t {threads} {params.extra_args} {params.input_args}
        gfatools gfa2fa {params.prefix}.p_ctg.gfa > {params.prefix}.p_ctg.fa
        ln -s {wildcards.sample}.p_ctg.fa {output.contigs}
        """


rule metamdbg:
    input:
        reads=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_files(wildcards.sample),
    output:
        contigs="analysis/{sample}/yeat/metamdbg/{label}/contigs.fasta",
    threads: 128
    params:
        outdir="analysis/{sample}/yeat/metamdbg/{label}",
        input_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .input_args(wildcards.sample),
        extra_args=lambda wildcards: config["asm_cfg"]
        .assemblers[wildcards.label]
        .extra_args,
    shell:
        """
        metaMDBG asm --out-dir {params.outdir} {params.input_args} -t {threads} {params.extra_args}
        gunzip {params.outdir}/contigs.fasta.gz
        """


rule quast:
    input:
        contigs="analysis/{sample}/yeat/{algorithm}/{label}/contigs.fasta",
    output:
        report="analysis/{sample}/yeat/{algorithm}/{label}/quast/report.html",
    params:
        outdir="analysis/{sample}/yeat/{algorithm}/{label}/quast",
    log:
        "analysis/{sample}/yeat/{algorithm}/{label}/quast/quast.log",
    shell:
        """
        quast.py {input.contigs} -o {params.outdir} > {log} 2>&1
        """


rule bandage:
    input:
        contigs="analysis/{sample}/yeat/{algorithm}/{label}/contigs.fasta",
    output:
        status="analysis/{sample}/yeat/{algorithm}/{label}/bandage/.done",
    params:
        outdir="analysis/{sample}/yeat/{algorithm}/{label}/bandage",
    run:
        gfa_files = (
            config["asm_cfg"].assemblers[wildcards.label].gfa_files(wildcards.sample)
        )
        for gfa in gfa_files:
            filename = Path(gfa).stem
            shell("Bandage image {gfa} {params.outdir}/{filename}.jpg")
        shell("touch {output.status}")
