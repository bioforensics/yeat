# -------------------------------------------------------------------------------------------------
# Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

import pytest
import re
from yeat.cli.yeat_auto import get_parser, main
from yeat.config.auto_pop import AutoPopError
from yeat.tests import data_file

pytestmark = pytest.mark.short


SHORT_READS = [data_file("short_reads_1.fastq.gz"), data_file("short_reads_2.fastq.gz")]
ANIMAL_READS = [data_file("Animal_289_R1.fq.gz"), data_file("Animal_289_R2.fq.gz")]
ALL_READS = SHORT_READS + ANIMAL_READS


def run_yeat_auto(arglist):
    args = get_parser().parse_args(arglist)
    main(args)


def compare_config_data(observed, expected):
    observed_data = observed.strip()
    with open(expected, "r") as f:
        expected_data = f.read().strip()
    expected_data = re.sub(r"yeat\/tests\/data", f'{data_file("")}', expected_data)
    assert observed_data == expected_data


@pytest.mark.parametrize(
    "sequences,expected",
    [
        (["short_reads"], data_file("configs/auto_one_sample.cfg")),
        (["short_reads", "Animal_289"], data_file("configs/auto_two_samples.cfg")),
        ([data_file("one_sample.txt")], data_file("configs/auto_one_sample.cfg")),
        ([data_file("two_samples.txt")], data_file("configs/auto_two_samples.cfg")),
    ],
)
def test_yeat_auto_with_seq_path(sequences, expected, capsys):
    arglist = sequences + ["--seq-path", data_file("")]
    run_yeat_auto(arglist)
    out, err = capsys.readouterr()
    compare_config_data(out, expected)


def test_bad_input_seq_path():
    arglist = ["short_reads", "--seq-path", "DNE"]
    with pytest.raises(FileNotFoundError):
        run_yeat_auto(arglist)


def test_sequence_with_no_files():
    sample_name = "SAMPLE_NAME_WITHOUT_READS"
    arglist = [sample_name, "--seq-path", data_file("")]
    message = f"sample {sample_name}: expected 2 FASTQ files for paired-end data, found 0"
    with pytest.raises(AutoPopError, match=message):
        run_yeat_auto(arglist)


@pytest.mark.parametrize(
    "sequences,files,expected",
    [
        (["short_reads"], SHORT_READS, data_file("configs/auto_one_sample.cfg")),
        (["short_reads", "Animal_289"], ALL_READS, data_file("configs/auto_two_samples.cfg")),
        ([data_file("one_sample.txt")], SHORT_READS, data_file("configs/auto_one_sample.cfg")),
        ([data_file("two_samples.txt")], ALL_READS, data_file("configs/auto_two_samples.cfg")),
    ],
)
def test_yeat_auto_with_files(sequences, files, expected, capsys):
    arglist = sequences + ["--files"] + files
    run_yeat_auto(arglist)
    out, err = capsys.readouterr()
    compare_config_data(out, expected)


def test_not_enough_input_files():
    arglist = ["short_reads", "--files", data_file("short_reads_1.fastq.gz")]
    message = "sample short_reads: expected 2 FASTQ files for paired-end data, found 1"
    with pytest.raises(AutoPopError, match=message):
        run_yeat_auto(arglist)


@pytest.mark.parametrize(
    "files",
    [
        (["DNE", data_file("short_reads_1.fastq.gz")]),
        ([data_file("short_reads_1.fastq.gz"), "DNE"]),
    ],
)
def test_bad_input_files(files):
    arglist = ["short_reads", "--files"] + files
    with pytest.raises(FileNotFoundError):
        run_yeat_auto(arglist)


def test_only_files_or_seq_path_in_command(capsys):
    arglist = ["short_reads", "--seq-path", data_file(""), "--files"] + SHORT_READS
    with pytest.raises(SystemExit):
        run_yeat_auto(arglist)
    out, err = capsys.readouterr()
    assert "error: argument --files: not allowed with argument --seq-path" in err


def test_sample_name_within_sample():
    arglist = ["short", "short_reads", "--seq-path", data_file("")]
    message = "cannot correctly process a sample name that is a substring of another sample name: short vs. short_reads"
    with pytest.raises(AutoPopError, match=message):
        run_yeat_auto(arglist)
