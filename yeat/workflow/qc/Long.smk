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
        read=lambda wc: config["asm_cfg"].get_sample_input_files(wc.sample, wc.platform),
    output:
        read="analysis/{sample}/qc/{platform}/read.fastq.gz",
    wildcard_constraints:
        platform="ont_simplex|ont_duplex|ont_ultralong|pacbio_hifi",
    params:
        do_copy=config["copy_input"],
    run:
        copy_input(input.read[0], output.read, params.do_copy)


rule fastqc:
    input:
        read=rules.copy_input.output.read,
    output:
        html="analysis/{sample}/qc/{platform}/fastqc/read_fastqc.html",
    wildcard_constraints:
        platform="ont_simplex|ont_duplex|ont_ultralong|pacbio_hifi",
    threads: config["threads"]
    params:
        outdir="analysis/{sample}/qc/{platform}/fastqc",
    log:
        "analysis/{sample}/qc/{platform}/fastqc/fastqc.log",
    shell:
        """
        fastqc -t {threads} -o {params.outdir} {input.read} > {log} 2>&1
        """


rule chopper:
    input:
        read=rules.copy_input.output.read,
    output:
        read="analysis/{sample}/qc/{platform}/chopper/read.fastq.gz",
    wildcard_constraints:
        platform="ont_simplex|ont_duplex|ont_ultralong|pacbio_hifi",
    threads: config["threads"]
    params:
        symlink_read="../read.fastq.gz",
        filter_enabled=lambda wc: config["asm_cfg"].get_sample_filter_enabled(wc.sample, "long"),
        filter_args=lambda wc: config["asm_cfg"].get_sample_filter_args(wc.sample, "long"),
    log:
        "analysis/{sample}/qc/{platform}/chopper/chopper.log",
    run:
        if not params.filter_enabled:
            Path(output.read).symlink_to(params.symlink_read)
            return
        shell("chopper -t {threads} -i {input.read} {params.filter_args} 2> {log} | gzip > {output.read}")


rule estimate_genome_size:
    input:
        read=rules.chopper.output.read,
    output:
        mash_sentinel=touch("analysis/{sample}/qc/{platform}/mash/sentinel.done"),
    wildcard_constraints:
        platform="ont_simplex|ont_duplex|ont_ultralong|pacbio_hifi",
    params:
        min_copies=2,
        sketch="analysis/{sample}/qc/{platform}/mash/reference.msh",
        mash_report="analysis/{sample}/qc/{platform}/mash/report.tsv",
        genome_size=lambda wc: config["asm_cfg"].get_sample_genome_size(wc.sample, "long"),
    log:
        "analysis/{sample}/qc/{platform}/mash/mash.log",
    run:
        if isinstance(params.genome_size, int):
            return
        shell("mash sketch -m {params.min_copies} -r {input.read} -o {params.sketch} > {log} 2>&1")
        shell("mash info -t {params.sketch} > {params.mash_report}")


rule seqkit:
    input:
        read=rules.chopper.output.read,
    output:
        seqkit_report="analysis/{sample}/qc/{platform}/seqkit/report.tsv",
    wildcard_constraints:
        platform="ont_simplex|ont_duplex|ont_ultralong|pacbio_hifi",
    shell:
        """
        seqkit stats {input} > {output.seqkit_report}
        """


rule downsample:
    input:
        read=rules.chopper.output.read,
        mash_sentinel=rules.estimate_genome_size.output.mash_sentinel,
        seqkit_report=rules.seqkit.output.seqkit_report,
    output:
        read="analysis/{sample}/qc/{platform}/downsample/read.fastq.gz",
    wildcard_constraints:
        platform="ont_simplex|ont_duplex|ont_ultralong|pacbio_hifi",
    threads: config["threads"]
    params:
        symlink_read="../chopper/read.fastq.gz",
        mash_report="analysis/{sample}/qc/{platform}/mash/report.tsv",
        outdir="analysis/{sample}/qc/{platform}/downsample",
        seed=config["seed"],
        downsample_enabled=lambda wc: config["asm_cfg"].get_sample_downsample_enabled(wc.sample, "long"),
        target_depth=lambda wc: config["asm_cfg"].get_sample_target_depth(wc.sample, "long"),
        target_num_reads=lambda wc: config["asm_cfg"].get_sample_target_num_reads(wc.sample, "long"),
        genome_size=lambda wc: config["asm_cfg"].get_sample_genome_size(wc.sample, "long"),
    log:
        "analysis/{sample}/qc/{platform}/downsample/bbnorm.log",
    run:
        if not params.downsample_enabled:
            Path(output.read).symlink_to(params.symlink_read)
            return
        downsample = Downsample.parse_data(params.target_depth, params.target_num_reads, params.genome_size, params.mash_report, input.seqkit_report, "long")
        shell("seqtk sample -s {params.seed} {input.read} {downsample.target_num_reads} | gzip > {params.outdir}/read.fastq.gz")
