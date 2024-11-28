import simpleapp
from simpleapp.pipeline import Pipeline, textinfile, textoutfile

def process(txt, args):
    return txt

def main(argv=None):
    parser = simpleapp.ArgumentParser(prog="nothing")
    parser.add_argument("infiles",nargs="+",help="Input file")
    parser.add_argument("-o","--outfile",help="Output file")
    parser.add_argument('-l','--logging',help="Logging level [DEBUG, INFO, WARN, ERROR, number]")
    parser.add_argument('--logfile',default='nothing.log',help='Set logging file')
    args = parser.parse_args(argv)

    Pipeline(args, textinfile, process, textoutfile, logging=True, defaultext="_output")

if __name__ == "__main__":
    main()

