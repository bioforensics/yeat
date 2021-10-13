import argparse


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-r1",
        type=str,
        nargs=1,
        metavar="file_name",
        default=None,
        help="read 1",
    )
    parser.add_argument(
        "-r2",
        type=str,
        nargs=1,
        metavar="file_name",
        default=None,
        help="read 2; for pair-end reads",
    )
    parser.add_argument(
        "-o",
        type=str,
        nargs=1,
        metavar="file_name",
        default=None,
        help="outfile",
    )

    args = parser.parse_args()

    # if args.r1 == None:
    #     print("hello")

    cmd = ["snakemake", "quast/Animal_289/report.html", "--cores", "4"]
    print(" ".join(cmd))
