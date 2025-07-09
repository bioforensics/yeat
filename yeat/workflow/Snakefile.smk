# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from yeat.config.config import AssemblyConfiguration


print(config)
assert 0

asm_cfg = AssemblyConfiguration.parse_toml(config["config"])
config["asm_cfg"] = asm_cfg



include: "Assemblers.smk"


rule all:
    input:
        asm_cfg.assembly_targets


module qc_paired_workflow:
    snakefile: "qc/Paired.smk"
    config: config

use rule * from qc_paired_workflow as qc_paired_*


module qc_single_workflow:
    snakefile: "qc/Single.smk"
    config: config

use rule * from qc_single_workflow as qc_single_*


module qc_long_workflow:
    snakefile: "qc/Long.smk"
    config: config

use rule * from qc_long_workflow as qc_long_*








# module shared_workflow:
#     snakefile: "Shared.smk"
#     config: config

# use rule * from shared_workflow as shared_*


# module paired_workflow:
#     snakefile: "Paired.smk"
#     config: config

# use rule * from paired_workflow as paired_*


# module single_workflow:
#     snakefile: "Single.smk"
#     config: config

# use rule * from single_workflow as single_*


# module oxford_workflow:
#     snakefile: "Oxford.smk"
#     config: config

# use rule * from oxford_workflow as oxford_*


# module pacbio_workflow:
#     snakefile: "Pacbio.smk"
#     config: config

# use rule * from pacbio_workflow as pacbio_*


# module hybrid_workflow:
#     snakefile: "Hybrid.smk"
#     config: config

# use rule * from hybrid_workflow as hybrid_*


# module bandage_workflow:
#     snakefile: "Bandage"
#     config: config

# use rule * from bandage_workflow as bandage_*



