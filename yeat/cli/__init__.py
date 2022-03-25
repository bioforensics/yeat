from .cli import get_parser, run_spades
from yeat.assembly import config


def main(args=None):
    if args is None:
        args = get_parser().parse_args()
    assert len(args.reads) == 2
    with open(args.config, "r") as fh:
        assemblers = config.AssemblyConfiguration.parse_json(fh)
    for assembler in assemblers:
        if assembler.algorithm == "spades":
            run_spades(
                *args.reads,
                outdir=args.outdir,
                cores=args.threads,
                sample=args.sample,
                dryrun=args.dry_run,
            )
