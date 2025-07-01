# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from yeat.workflow.aux import copy_input


rule copy_input:
    input:
        read=lambda wildcards: getattr(config["config"].samples[wildcards.sample], (wildcards.platform)),
    output:
        read="analysis/{sample}/qc/{platform}/read.fastq.gz",
    wildcard_constraints:
        platform="ont|pacbio",
    params:
        do_copy=config["copy_input"],
    run:
        copy_input(input.read, output.read, params.do_copy)



rule fastqc:
    input:
        read=rules.copy_input.output.read,
    output:
        html="analysis/{sample}/qc/{platform}/fastqc/read_fastqc.html"
    wildcard_constraints:
        platform="ont|pacbio",
    threads: 128
    params:
        outdir="analysis/{sample}/qc/{platform}/fastqc"
    log:
        "analysis/{sample}/qc/{platform}/fastqc/fastqc.log"
    shell:
        """
        fastqc {input.read} -t {threads} -o {params.outdir} > {log} 2>&1
        """


rule chopper:
    input:
        read=rules.copy_input.output.read,
    output:
        read="analysis/{sample}/qc/{platform}/chopper/read.fastq.gz",
    wildcard_constraints:
        platform="ont|pacbio",
    threads: 128
    params:
        skip_filter=config["skip_filter"],
        symlink_read="../read.fastq.gz",
        args=f"-q {config['quality']} -l {config['min_length']}",
        raw_x_label="Raw Read Length",
        filtered_x_label="Filtered Read Length",
        raw_png="analysis/{sample}/magenta/{platform}/qc/chopper/raw_rld.png",
        filtered_png="analysis/{sample}/magenta/{platform}/qc/chopper/filtered_rld.png",
    run:
        if params.skip_filter:
            Path(output.read).symlink_to(params.symlink_read)
            return
        shell("chopper {params.args} -i {input.read} | gzip > {output.read}")


# calculate the genomesize?


rule downsample:
    input:
        read=rules.chopper.output.read,
    output:
        read="analysis/{sample}/qc/{platform}/downsample/read.fastq.gz",
    wildcard_constraints:
        platform="ont|pacbio",
    params:
        # down=config["down"],
        # seed=config["seed"],
        downsample=lambda wildcards: config["config"].samples[wildcards.sample].downsample,
        symlink_read="../chopper/read.fastq.gz",
    threads: 8
    run:
        if params.downsample == -1:
            Path(output.read).symlink_to(params.symlink_read)
            return
        
        # shell("seqtk sample -s {params.seed} {input.read} {params.down} | gzip > {output.read}")