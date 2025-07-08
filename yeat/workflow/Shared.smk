# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

rule quast:
    output:
        report="analysis/{sample}/{readtype}/{label}/{assembler}/quast/report.html"
    input:
        contigs="analysis/{sample}/{readtype}/{label}/{assembler}/contigs.fasta"
    params:
        outdir="analysis/{sample}/{readtype}/{label}/{assembler}/quast"
    log:
        "analysis/{sample}/{readtype}/{label}/{assembler}/quast/quast.log"
    shell:
        """
        quast.py {input.contigs} -o {params.outdir} > {log} 2>&1
        """
