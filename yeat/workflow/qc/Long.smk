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
    log:
        "analysis/{sample}/qc/{platform}/chopper/chopper.log",
    run:
        if params.skip_filter:
            Path(output.read).symlink_to(params.symlink_read)
            return
        shell("chopper -t {threads} -q {params.quality} -l {params.min_length} -i {input.read} 2> {log} | gzip > {output.read}")


rule estimate_genome_size:
    input:
        read=rules.chopper.output.read,
    output:
        mash_sentinel="analysis/{sample}/qc/{platform}/mash/sentinel.done",
        seqkit_sentinel="analysis/{sample}/qc/{platform}/seqkit/sentinel.done",
    wildcard_constraints:
        platform="ont_simplex|ont_duplex|ont_ultralong|pacbio_hifi",
    params:
        min_copies=2,
        sketch="analysis/{sample}/qc/{platform}/mash/reference.msh",
        mash_report="analysis/{sample}/qc/{platform}/mash/report.tsv",
        seqkit_report="analysis/{sample}/qc/{platform}/seqkit/report.tsv",
        genome_size=lambda wc: config["asm_cfg"].get_sample_genome_size(wc.sample),
    log:
        "analysis/{sample}/qc/{platform}/mash/mash.log",
    run:
        if params.genome_size:
            shell("touch {output.mash_sentinel} {output.seqkit_sentinel}")
            return
        shell("mash sketch -m {params.min_copies} -r {input.read} -o {params.sketch} > {log} 2>&1")
        shell("mash info -t {params.sketch} > {params.mash_report}")
        shell("touch {output.mash_sentinel}")
        shell("seqkit stats {input} > {params.seqkit_report}")
        shell("touch {output.seqkit_sentinel}")


rule downsample:
    input:
        read=rules.chopper.output.read,
        mash_sentinel=rules.estimate_genome_size.output.mash_sentinel,
        seqkit_sentinel=rules.estimate_genome_size.output.seqkit_sentinel,
    output:
        read="analysis/{sample}/qc/{platform}/downsample/read.fastq.gz",
    wildcard_constraints:
        platform="ont_simplex|ont_duplex|ont_ultralong|pacbio_hifi",
    threads: 128
    params:
        symlink_read="../chopper/read.fastq.gz",
        mash_report="analysis/{sample}/qc/{platform}/mash/report.tsv",
        seqkit_report="analysis/{sample}/qc/{platform}/seqkit/report.tsv",
        outdir="analysis/{sample}/qc/{platform}/downsample",
        seed=config["seed"],
        downsampling=lambda wc: config["asm_cfg"].get_sample_downsampling(wc.sample),
        target_num_reads=lambda wc: config["asm_cfg"].get_sample_target_num_reads(wc.sample),
        genome_size=lambda wc: config["asm_cfg"].get_sample_genome_size(wc.sample),
        target_depth=lambda wc: config["asm_cfg"].get_sample_target_depth(wc.sample),
    log:
        "analysis/{sample}/qc/{platform}/downsample/bbnorm.log",
    run:
        if params.downsampling == "none":
            Path(output.read).symlink_to(params.symlink_read)
            return
        if params.target_num_reads:
            num_reads = params.target_num_reads
        else:
            downsample = Downsample.parse_data(params.mash_report, params.seqkit_report, params.target_num_reads, params.genome_size, params.target_depth)
            num_reads = downsample.get_num_reads(paired=False)
        shell("seqtk sample -s {params.seed} {input.read} {num_reads} | gzip > {params.outdir}/read.fastq.gz")
