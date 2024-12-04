#!/usr/bin/env python3

import simpleapp, codecs
from simpleapp.pipeline import Pipeline, textinfile, textoutfile

def process(txt, args):
    if args.reverse:
        res = txt.encode('raw_unicode_escape').decode('utf-8')
    else:
        res = txt.encode('utf-8').decode('raw_unicode_escape')
    return res

def main(argv=None):
    parser = simpleapp.ArgumentParser(prog="uniraw")
    parser.add_argument("infiles",nargs="+",help="Input file")
    parser.add_argument("-o","--outfile",default="*_uni",help="Output file")
    parser.add_argument("-r","--reverse",action="store_true",help="Expand out Unicode chars")
    args = parser.parse_args(argv)

    Pipeline(args, textinfile, process, textoutfile)

if __name__ == "__main__":
    main()

