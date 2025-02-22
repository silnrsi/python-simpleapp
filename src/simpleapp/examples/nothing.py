from simpleapp import *

def process(txt, args):
    return txt

def main(argv=None):
    parser = ArgumentParser(prog="nothing", logging=True)
    parser.add_argument("infiles",nargs="+",help="Input file")
    parser.add_argument("-o","--outfile",help="Output file")
    args = parser.parse_args(argv)

    Pipeline(args, textinfile, process, textoutfile)

if __name__ == "__main__":
    main()

