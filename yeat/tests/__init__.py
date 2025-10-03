# -------------------------------------------------------------------------------------------------
# Copyright (c) 2021, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from importlib.resources import files
import multiprocessing
from pathlib import Path
from yeat.cli import main, cli
from yeat.config.assemblers import ALGORITHM_CONFIGS
from yeat.config.config import AssemblyConfiguration
from yeat.workflow import get_config_data


FINAL_FILES = {
    "spades": "contigs.fasta",
    "megahit": "final.contigs.fa",
    "unicycler": "assembly.fasta",
    "penguin": "contigs.fasta",
    "flye": "assembly.fasta",
    "canu": "*.contigs.fasta",
    "hifiasm": "asm.bp.p_ctg.fa",
    "hifiasm_meta": "asm.p_ctg.fa",
    "metamdbg": "contigs.fasta",
    "verkko": "assembly.fasta",
    "myloasm": "assembly_primary.fa",
}


def data_file(path):
    pkg_path = files("yeat") / f"tests/data/{path}"
    return str(pkg_path)


def get_core_count():
    return multiprocessing.cpu_count()


def run_yeat(arglist):
    arglist = map(str, arglist)
    args = cli.get_parser().parse_args(arglist)
    main(args)


def final_contig_files_exist(wd, config_path):
    cfg_data = get_config_data(config_path)
    config = AssemblyConfiguration.parse_snakemake_config(cfg_data)
    reversed_dict = {v: k for k, v in ALGORITHM_CONFIGS.items()}
    for assembler_label, assembler in config.assemblers.items():
        assembler_type = type(assembler)
        algo_key = reversed_dict[assembler_type]
        contig_file = FINAL_FILES[algo_key]
        for sample_label in assembler.samples:
            search_dir = Path(f"{wd}/analysis/{sample_label}/yeat/{algo_key}/{assembler_label}")
            matches = list(search_dir.glob(contig_file))
            assert len(matches) == 1
