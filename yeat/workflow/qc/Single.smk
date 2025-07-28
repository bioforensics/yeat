# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from yeat.workflow.qc.aux import copy_input


rule copy_input:
    input:
        read=lambda wildcards: config["asm_cfg"].samples[wildcards.sample].data["illumina"],
    output:
        read="analysis/{sample}/qc/illumina/read.fastq.gz",
    params:
        do_copy=config["copy_input"],
    run:
        copy_input(input.read[0], output.read, params.do_copy)


rule fastqc:
    input:
        read=rules.copy_input.output.read,
    output:
        html="analysis/{sample}/qc/illumina/fastqc/read_fastqc.html",
    threads: 128
    params:
        outdir="analysis/{sample}/qc/illumina/fastqc",
    log:
        "analysis/{sample}/qc/illumina/fastqc/fastqc.log",
    shell:
        """
        fastqc -t {threads} -o {params.outdir} {input.read} > {log} 2>&1
        """


rule fastp:
    input:
        read=rules.copy_input.output.read,
    output:
        read="analysis/{sample}/qc/illumina/fastp/read.fastq.gz",
    params:
        symlink_read="../read.fastq.gz",
        html_report="analysis/{sample}/qc/illumina/fastp/fastp.html",
        json_report="analysis/{sample}/qc/illumina/fastp/fastp.json",
        txt_report="analysis/{sample}/qc/illumina/fastp/report.txt",
        skip_filter=lambda wildcards: config["asm_cfg"].samples[wildcards.sample].skip_filter,
        min_length=lambda wildcards: config["asm_cfg"].samples[wildcards.sample].min_length,
    run:
        if params.skip_filter:
            Path(output.read).symlink_to(params.symlink_read)
            return
        cmd = "fastp -i {input.read} -o {output.read} -l {params.min_length} --detect_adapter_for_pe --html {params.html_report} --json {params.json_report} 2> {params.txt_report}"
        shell(cmd)


rule mash:
    input:
        read=rules.copy_input.output.read,
    output:
        sketch="analysis/{sample}/qc/illumina/mash/read.fastq.gz.msh",
        mash_report="analysis/{sample}/qc/illumina/mash/report.tsv",
    shell:
        """
        mash sketch {input.read} -o {output.sketch}
        mash info -t {output.sketch} > {output.mash_report}
        """


rule downsample:
    input:
        read=rules.fastp.output.read,
        mash_report=rules.mash.output.mash_report,
    output:
        read="analysis/{sample}/qc/illumina/downsample/read.fastq.gz",
    params:
        symlink_read="../read.fastq.gz",
        fastp_report="analysis/{sample}/qc/illumina/fastp/fastp.json",
        outdir="analysis/{sample}/qc/illumina/downsample",
        seed=config["seed"],
        downsample=lambda wildcards: config["asm_cfg"].samples[wildcards.sample].downsample,
        genome_size=lambda wildcards: config["asm_cfg"].samples[wildcards.sample].genome_size,
        coverage_depth=lambda wildcards: config["asm_cfg"].samples[wildcards.sample].coverage_depth,
    run:
        if params.downsample == -1:
            Path(output.read).symlink_to(params.symlink_read)
            return
        genome_size = get_genome_size(params.genome_size, input.mash_report)
        average_read_length = get_average_read_length(params.fastp_report)
        down = get_down(params.downsample, genome_size, params.coverage_depth, average_read_length)
        print_downsample_values(genome_size, average_read_length, params.coverage_depth, down, seed)
        shell("seqtk sample -s {params.seed} {input.read1} {down} | gzip > {params.outdir}/read.fastq.gz")
