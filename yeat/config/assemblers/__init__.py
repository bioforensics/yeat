# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .canu import CanuAssembler
from .flye import FlyeAssembler
from .hifiasm import HifiasmAssembler
from .hifiasm_meta import HifiasmMetaAssembler
from .megahit import MEGAHITAssembler
from .metamdbg import MetaMDBGAssembler
from .penguin import PenguiNAssembler
from .spades import SPAdesAssembler
from .unicycler import UnicyclerAssembler
from .velvet import VelvetAssembler


ALGORITHM_CONFIGS = {
    "spades": SPAdesAssembler,
    "megahit": MEGAHITAssembler,
    "unicycler": UnicyclerAssembler,
    "penguin": PenguiNAssembler,
    "velvet": VelvetAssembler,
    "canu": CanuAssembler,
    "flye": FlyeAssembler,
    "hifiasm": HifiasmAssembler,
    "hifiasm_meta": HifiasmMetaAssembler,
    "metamdbg": MetaMDBGAssembler,
}


def select(algorithm):
    if algorithm not in ALGORITHM_CONFIGS:
        raise KeyError(f"unknown assembly algorithm {algorithm}")
    return ALGORITHM_CONFIGS[algorithm]
