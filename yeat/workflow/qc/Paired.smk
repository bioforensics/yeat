# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from yeat.workflow.qc.aux import copy_input
from yeat.workflow.qc.downsample import Downsample


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
    threads: config['threads']
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
        filter_enabled=lambda wc: config["asm_cfg"].get_sample_filter_enabled(wc.sample, "short"),
        filter_args=lambda wc: config["asm_cfg"].get_sample_filter_args(wc.sample, "short"),
    run:
        if not params.filter_enabled:
            Path(output.r1).symlink_to(params.symlink_r1)
            Path(output.r2).symlink_to(params.symlink_r2)
            return
        cmd = "fastp -i {input.r1} -I {input.r2} -o {output.r1} -O {output.r2} --html {params.html_report} --json {params.json_report} {params.filter_args} 2> {params.txt_report}"
        shell(cmd)


rule estimate_genome_size:
    input:
        r1=rules.fastp.output.r1,
        r2=rules.fastp.output.r2,
    output:
        mash_sentinel=touch("analysis/{sample}/qc/illumina/mash/sentinel.done"),
    params:
        min_copies=2,
        sketch="analysis/{sample}/qc/illumina/mash/reference.msh",
        mash_report="analysis/{sample}/qc/illumina/mash/report.tsv",
        genome_size=lambda wc: config["asm_cfg"].get_sample_genome_size(wc.sample, "short"),
    log:
        "analysis/{sample}/qc/illumina/mash/mash.log",
    run:
        if isinstance(params.genome_size, int):
            return
        shell("mash sketch -m {params.min_copies} -r {input.r1} {input.r2} -o {params.sketch} > {log} 2>&1")
        shell("mash info -t {params.sketch} > {params.mash_report}")


rule seqkit:
    input:
        r1=rules.fastp.output.r1,
        r2=rules.fastp.output.r2,
    output:
        seqkit_report="analysis/{sample}/qc/illumina/seqkit/report.tsv",
    shell:
        """
        seqkit stats {input} > {output.seqkit_report}
        """


rule downsample:
    input:
        r1=rules.fastp.output.r1,
        r2=rules.fastp.output.r2,
        mash_sentinel=rules.estimate_genome_size.output.mash_sentinel,
        seqkit_report=rules.seqkit.output.seqkit_report,
    output:
        r1="analysis/{sample}/qc/illumina/downsample/R1.fastq.gz",
        r2="analysis/{sample}/qc/illumina/downsample/R2.fastq.gz",
    threads: config['threads']
    params:
        symlink_r1="../R1.fastq.gz",
        symlink_r2="../R2.fastq.gz",
        mash_report="analysis/{sample}/qc/illumina/mash/report.tsv",
        outdir="analysis/{sample}/qc/illumina/downsample",
        seed=config["seed"],
        downsample_enabled=lambda wc: config["asm_cfg"].get_sample_downsample_enabled(wc.sample, "short"),
        downsample_method=lambda wc: config["asm_cfg"].get_sample_downsample_method(wc.sample, "short"),
        target_depth=lambda wc: config["asm_cfg"].get_sample_target_depth(wc.sample, "short"),
        target_num_reads=lambda wc: config["asm_cfg"].get_sample_target_num_reads(wc.sample, "short"),
        genome_size=lambda wc: config["asm_cfg"].get_sample_genome_size(wc.sample, "short"),
    log:
        "analysis/{sample}/qc/illumina/downsample/bbnorm.log",
    run:
        if not params.downsample_enabled:
            Path(output.r1).symlink_to(params.symlink_r1)
            Path(output.r2).symlink_to(params.symlink_r2)
            return
        if params.downsample_method == "random":
            downsample = Downsample.parse_data(params.target_depth, params.target_num_reads, params.genome_size, params.mash_report, input.seqkit_report, "paired")
            shell("seqtk sample -s {params.seed} {input.r1} {downsample.target_num_reads} | gzip > {params.outdir}/R1.fastq.gz")
            shell("seqtk sample -s {params.seed} {input.r2} {downsample.target_num_reads} | gzip > {params.outdir}/R2.fastq.gz")
        elif params.downsample_method == "bbnorm":
            shell("bbnorm.sh threads={threads} in={input.r1} in2={input.r2} out={params.outdir}/R1.fastq.gz out2={params.outdir}/R2.fastq.gz target={params.target_depth} > {log} 2>&1")
