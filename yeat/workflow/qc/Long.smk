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
    threads: 128
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
    threads: 128
    params:
        symlink_read="../read.fastq.gz",
        skip_filter=lambda wc: config["asm_cfg"].get_sample_skip_filter(wc.sample),
        quality=lambda wc: config["asm_cfg"].get_sample_quality(wc.sample),
        min_length=lambda wc: config["asm_cfg"].get_sample_min_length(wc.sample),
    run:
        if params.skip_filter:
            Path(output.read).symlink_to(params.symlink_read)
            return
        shell("chopper -t {threads} -q {params.quality} -l {params.min_length} -i {input.read} | gzip > {output.read}")


rule downsample:
    input:
        read=rules.chopper.output.read,
    output:
        read="analysis/{sample}/qc/{platform}/downsample/read.fastq.gz",
    wildcard_constraints:
        platform="ont_simplex|ont_duplex|ont_ultralong|pacbio_hifi",
    params:
        symlink_read="../chopper/read.fastq.gz",
        seed=config["seed"],
        target_num_reads=lambda wc: config["asm_cfg"].get_sample_target_num_reads(wc.sample),
    run:
        if params.target_num_reads == -1:
            Path(output.read).symlink_to(params.symlink_read)
            return
        shell("seqtk sample -s {params.seed} {input.read} {params.target_num_reads} | gzip > {output.read}")
