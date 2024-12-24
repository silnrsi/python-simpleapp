#!/usr/bin/python3

from simpleapp import changes
from simpleapp.pipeline import Pipeline, textinfile, textoutfile

def main(argv=None):
    parser = simpleapp.ArgumentParser(prog='runregchanges', logging=True)
    parser.add_argument("infiles",nargs="+",help="Input file")
    parser.add_argument("-c","--changes",required=True,help="changes.txt")
    parser.add_argument("-o","--outfile",help="Output file")
    args = parser.parse_args(argv)

    c = changes.Changes(args.changes)
    Pipeline(args.infiles, args.outfile, args, textinfile, c.runChanges,
             textoutfile, defaultext="_changed")

if __name__ == "__main__":
    main()
