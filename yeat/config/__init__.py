# -------------------------------------------------------------------------------------------------
# Copyright (c) 2023, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

ILLUMINA_READS = ("paired", "single")
PACBIO_READS = ("pacbio-raw", "pacbio-corr", "pacbio-hifi")
OXFORD_READS = ("nano-raw", "nano-corr", "nano-hq")
LONG_READS = PACBIO_READS + OXFORD_READS
READ_TYPES = ILLUMINA_READS + LONG_READS


class AssemblyConfigError(ValueError):
    pass
