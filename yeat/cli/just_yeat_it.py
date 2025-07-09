# # -------------------------------------------------------------------------------------------------
# # Copyright (c) 2024, DHS. This file is part of YEAT: http://github.com/bioforensics/yeat
# #
# # This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# # Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# # National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# # Development Center.
# # -------------------------------------------------------------------------------------------------

# from . import cli, illumina
# from argparse import ArgumentParser
# import json
# from pathlib import Path
# from yeat import workflow


# def main(args=None):
#     if args is None:
#         args = get_parser().parse_args()  # pragma: no cover
#     create_config(args)
#     add_config(args)
#     if not args.grid:
#         setattr(args, "grid", False)
#     workflow.run_workflow(args)


# def get_parser(exit_on_error=True):
#     parser = ArgumentParser(exit_on_error=exit_on_error)
#     parser._optionals.title = "options"
#     cli.workflow_configuration(parser)
#     cli.grid_configuration(parser)
#     illumina.fastp_configuration(parser)
#     illumina.downsample_configuration(parser, just_yeat_it=True)
#     sample_configuration(parser)
#     algorithm_configuration(parser)
#     positional_args(parser)
#     return parser


# def sample_configuration(parser):
#     sample = parser.add_argument_group("sample configuration")
#     sample.add_argument(
#         "--sample-label",
#         default="sample1",
#         help='set the sample label; by default, "sample1"',
#         metavar="STR",
#     )


# def algorithm_configuration(parser):
#     algorithm = parser.add_argument_group("algorithm configuration")
#     algorithm.add_argument(
#         "--assembly-label",
#         default="assembly1",
#         help='set the assembly label; by default, "assembly1"',
#         metavar="STR",
#     )
#     algorithm.add_argument(
#         "--algorithm",
#         default="spades",
#         help='substitute the default assembly algorithm with another algorithm; for example, "megahit" or "unicycler"; by default, "spades"',
#         metavar="STR",
#     )
#     algorithm.add_argument(
#         "--extra-args",
#         default="",
#         help='add assembly algorithm flags; for example, "--meta" or "--isolate --careful" for SPAdes; by default, empty string',
#         metavar="STR",
#     )


# def positional_args(parser):
#     parser._positionals.title = "required arguments"
#     parser.add_argument("reads", type=str, nargs=2, help="paired-end reads in FASTQ format")


# def create_config(args):
#     data = get_config_data(args)
#     outdir = Path(args.outdir)
#     outdir.mkdir(parents=True, exist_ok=True)
#     outfile = open(outdir / "config.cfg", "w")
#     json.dump(data, outfile, indent=4)


# def get_config_data(args):
#     return {
#         "samples": {
#             args.sample_label: {
#                 "paired": [args.reads],
#                 "downsample": args.downsample,
#                 "genome_size": args.genome_size,
#                 "coverage_depth": args.coverage_depth,
#             },
#         },
#         "assemblies": {
#             args.assembly_label: {
#                 "algorithm": args.algorithm,
#                 "extra_args": args.extra_args,
#                 "samples": [args.sample_label],
#                 "mode": "paired",
#             }
#         },
#     }


# def add_config(args):
#     config = Path(args.outdir) / "config.cfg"
#     setattr(args, "config", str(config.resolve()))
