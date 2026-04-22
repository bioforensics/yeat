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
        read=lambda wc: config["asm_cfg"].get_sample_input_files(wc.sample, "illumina"),
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
        filter_enabled=lambda wc: config["asm_cfg"].get_sample_filter_enabled(wc.sample, "short"),
        filter_args=lambda wc: config["asm_cfg"].get_sample_filter_args(wc.sample, "short"),
    run:
        if not params.filter_enabled:
            Path(output.read).symlink_to(params.symlink_read)
            return
        cmd = "fastp -i {input.read} -o {output.read} --html {params.html_report} --json {params.json_report} {params.filter_args} 2> {params.txt_report}"
        shell(cmd)


rule estimate_genome_size:
    input:
        read=rules.fastp.output.read,
    output:
        mash_sentinel="analysis/{sample}/qc/illumina/mash/sentinel.done",
    params:
        min_copies=2,
        sketch="analysis/{sample}/qc/illumina/mash/reference.msh",
        mash_report="analysis/{sample}/qc/illumina/mash/report.tsv",
        genome_size=lambda wc: config["asm_cfg"].get_sample_genome_size(wc.sample, "short"),
    log:
        "analysis/{sample}/qc/illumina/mash/mash.log",
    run:
        if isinstance(params.genome_size, int):
            shell("touch {output.mash_sentinel}")
            return
        shell("mash sketch -m {params.min_copies} -r {input.read} -o {params.sketch} > {log} 2>&1")
        shell("mash info -t {params.sketch} > {params.mash_report}")
        shell("touch {output.mash_sentinel}")


rule seqkit:
    input:
        read=rules.fastp.output.read,
    output:
        seqkit_report="analysis/{sample}/qc/illumina/seqkit/report.tsv",
    shell:
        """
        seqkit stats {input} > {output.seqkit_report}
        """


rule downsample:
    input:
        read=rules.fastp.output.read,
        mash_sentinel=rules.estimate_genome_size.output.mash_sentinel,
        seqkit_report=rules.seqkit.output.seqkit_report,
    output:
        read="analysis/{sample}/qc/illumina/downsample/read.fastq.gz",
    threads: 128
    params:
        symlink_read="../read.fastq.gz",
        mash_report="analysis/{sample}/qc/illumina/mash/report.tsv",
        outdir="analysis/{sample}/qc/illumina/downsample",
        seed=config["seed"],
        downsample_method=lambda wc: config["asm_cfg"].get_sample_downsample_method(wc.sample, "short"),
        target_num_reads=lambda wc: config["asm_cfg"].get_sample_target_num_reads(wc.sample, "short"),
        genome_size=lambda wc: config["asm_cfg"].get_sample_genome_size(wc.sample, "short"),
        target_depth=lambda wc: config["asm_cfg"].get_sample_target_depth(wc.sample, "short"),
    log:
        "analysis/{sample}/qc/illumina/downsample/bbnorm.log",
    run:
        if not params.downsample_enabled:
            Path(output.read).symlink_to(params.symlink_read)
        if params.downsample_method == "random":
            downsample = Downsample.parse_data(params.target_num_reads, params.genome_size, params.target_depth, params.mash_report, input.seqkit_report)
            num_reads = downsample.get_num_reads(paired=False)
            shell("seqtk sample -s {params.seed} {input.read} {num_reads} | gzip > {params.outdir}/read.fastq.gz")
        elif params.downsample_method == "bbnorm":
            shell("bbnorm.sh threads={threads} in={input.read} out={params.outdir}/read.fastq.gz > {log} 2>&1")
