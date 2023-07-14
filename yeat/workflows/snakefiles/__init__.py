# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

def get_expected_files(short_qc=False, pacbio_qc=False, nanopore=False):
    inputlist = []
    for label in config["labels"]:
        assembler = config["assemblers"][label]
        for sample in config["label_to_samples"][label]:
            inputlist.append(f"analysis/{sample}/{label}/{assembler}/quast/{sample}_report.html")
    if short_qc:
        inputlist += expand("seq/fastqc/{sample}/{sample}_{reads}_fastqc.html", sample=[*config["samples"]], reads=["R1", "R2"])
    if pacbio_qc:
        inputlist += expand("seq/input/{sample}/fastqc/combined-reads_fastqc.html", sample=[*config["samples"]])
    if nanopore:
        inputlist += expand("seq/input/{sample}/highQuality-reads.fq.gz", sample=[*config["samples"]])
        inputlist += expand("seq/input/{sample}/nanoplot/{quality}_LengthvsQualityScatterPlot_dot.pdf", sample=[*config["samples"]], quality=["raw", "filtered"])
    return inputlist