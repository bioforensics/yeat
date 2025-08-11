# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from yeat.workflow.qc.aux import copy_input, get_genome_size, get_average_read_length, get_down, print_downsample_values


rule copy_input:
    input:
        reads=lambda wc: config["asm_cfg"].get_sample_input_files(wc.sample, "illumina"),
    output:
        r1="analysis/{sample}/qc/illumina/R1.fastq.gz",
        r2="analysis/{sample}/qc/illumina/R2.fastq.gz",
    params:
        do_copy=config["copy_input"],
    run:
        copy_input(input.reads[0], output.r1, params.do_copy)
        copy_input(input.reads[1], output.r2, params.do_copy)


rule fastqc:
    input:
        r1=rules.copy_input.output.r1,
        r2=rules.copy_input.output.r2,
    output:
        r1_html="analysis/{sample}/qc/illumina/fastqc/R1_fastqc.html",
        r2_html="analysis/{sample}/qc/illumina/fastqc/R2_fastqc.html",
    threads: 128
    params:
        outdir="analysis/{sample}/qc/illumina/fastqc",
    log:
        "analysis/{sample}/qc/illumina/fastqc/fastqc.log",
    shell:
        """
        fastqc -t {threads} -o {params.outdir} {input.r1} {input.r2} > {log} 2>&1
        """


rule fastp:
    input:
        r1=rules.copy_input.output.r1,
        r2=rules.copy_input.output.r2,
    output:
        r1="analysis/{sample}/qc/illumina/fastp/R1.fastq.gz",
        r2="analysis/{sample}/qc/illumina/fastp/R2.fastq.gz",
    params:
        symlink_r1="../R1.fastq.gz",
        symlink_r2="../R2.fastq.gz",
        html_report="analysis/{sample}/qc/illumina/fastp/fastp.html",
        json_report="analysis/{sample}/qc/illumina/fastp/fastp.json",
        txt_report="analysis/{sample}/qc/illumina/fastp/report.txt",
        skip_filter=lambda wc: config["asm_cfg"].get_sample_skip_filter(wc.sample),
        min_length=lambda wc: config["asm_cfg"].get_sample_min_length(wc.sample),
    run:
        if params.skip_filter:
            Path(output.r1).symlink_to(params.symlink_r1)
            Path(output.r2).symlink_to(params.symlink_r2)
            return
        cmd = "fastp -i {input.r1} -I {input.r2} -o {output.r1} -O {output.r2} -l {params.min_length} --detect_adapter_for_pe --html {params.html_report} --json {params.json_report} 2> {params.txt_report}"
        shell(cmd)


rule mash:
    input:
        r1=rules.copy_input.output.r1,
    output:
        sketch="analysis/{sample}/qc/illumina/mash/R1.fastq.gz.msh",
        mash_report="analysis/{sample}/qc/illumina/mash/report.tsv",
    shell:
        """
        mash sketch {input.r1} -o {output.sketch}
        mash info -t {output.sketch} > {output.mash_report}
        """


rule downsample:
    input:
        r1=rules.fastp.output.r1,
        r2=rules.fastp.output.r2,
        mash_report=rules.mash.output.mash_report,
    output:
        r1="analysis/{sample}/qc/illumina/downsample/R1.fastq.gz",
        r2="analysis/{sample}/qc/illumina/downsample/R2.fastq.gz",
    params:
        symlink_r1="../R1.fastq.gz",
        symlink_r2="../R2.fastq.gz",
        fastp_report="analysis/{sample}/qc/illumina/fastp/fastp.json",
        outdir="analysis/{sample}/qc/illumina/downsample",
        seed=config["seed"],
        downsample=lambda wc: config["asm_cfg"].get_sample_downsample(wc.sample),
        genome_size=lambda wc: config["asm_cfg"].get_sample_genome_size(wc.sample),
        coverage_depth=lambda wc: config["asm_cfg"].get_sample_coverage_depth(wc.sample),
    run:
        if params.downsample == -1:
            Path(output.r1).symlink_to(params.symlink_r1)
            Path(output.r2).symlink_to(params.symlink_r2)
            return
        genome_size = get_genome_size(params.genome_size, input.mash_report)
        average_read_length = get_average_read_length(params.fastp_report)
        down = get_down(params.downsample, genome_size, params.coverage_depth, average_read_length)
        print_downsample_values(genome_size, average_read_length, params.coverage_depth, down, seed)
        shell("seqtk sample -s {params.seed} {input.read1} {down} | gzip > {params.outdir}/R1.fastq.gz")
        shell("seqtk sample -s {params.seed} {input.read2} {down} | gzip > {params.outdir}/R2.fastq.gz")
