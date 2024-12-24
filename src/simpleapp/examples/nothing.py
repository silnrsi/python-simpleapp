import simpleapp
from simpleapp.pipeline import Pipeline, textinfile, textoutfile

def process(txt, args):
    return txt

def main(argv=None):
    parser = simpleapp.ArgumentParser(prog="nothing", logging=True)
    parser.add_argument("infiles",nargs="+",help="Input file")
    parser.add_argument("-o","--outfile",help="Output file")
    args = parser.parse_args(argv)

    Pipeline(args, textinfile, process, textoutfile, defaultext="_output")

if __name__ == "__main__":
    main()

