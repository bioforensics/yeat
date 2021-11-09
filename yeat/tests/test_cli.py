import yeat
from yeat import cli
import os
import pytest


def test_basic_run(tmp_path):
    wd = str(tmp_path)
    os.makedirs(wd, exist_ok=True)
    print(wd)

    # calls yeat with the input parameters
    # checks if the results of spades and quast, etc. are correct

    assert 0
