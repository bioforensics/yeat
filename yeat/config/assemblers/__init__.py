# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .spades import SPAdesAssembler


algorithm_configs = {
    "spades": SPAdesAssembler,
}


def select(algorithm):
    if algorithm not in algorithm_configs:
        raise KeyError(f"unknown assembly algorithm {algorithm}")
    return algorithm_configs[algorithm]
