# -------------------------------------------------------------------------------------------------
# Copyright (c) 2026, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
from yeat.config.downsample_settings import DownsampleSettings


@pytest.mark.parametrize("genome_size", ["3.5kb", "3.5 kb", "3.5 Kb", "3.5 KB", "3,500"])
def test_genome_size_kb(genome_size):
    ds = DownsampleSettings.parse_data({"genome_size": genome_size})
    assert ds.genome_size == 3500


@pytest.mark.parametrize("genome_size", ["3.5mb", "3.5 mb", "3.5 Mb", "3.5 MB", "3,500,000"])
def test_genome_size_mb(genome_size):
    ds = DownsampleSettings.parse_data({"genome_size": genome_size})
    assert ds.genome_size == 3500000


@pytest.mark.parametrize("genome_size", ["3.5gb", "3.5 gb", "3.5 Gb", "3.5 GB", "3,500,000,000"])
def test_genome_size_gb(genome_size):
    ds = DownsampleSettings.parse_data({"genome_size": genome_size})
    assert ds.genome_size == 3500000000
