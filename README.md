# simpleapp

simpleapp is a python module designed to make it easy to create simple
applications for sharing with colleagues who may not have python installed, etc.
The initial application area targetted is text processing and conversion. The
aim is to enable a relatively weak python programmer (who may only use python
occasionally) to be able to write some code to transform some data, but to not
to have to worry too much about how to turn what is basically a single function
into a full blow application.

The module uses the gooey module to provide a GUI for the command line options.

The two main areas where simpleapp helps is in providing a more sophisticated
drop in replacement for argparse (sitting between argparse and gooey) and a
pipeline function that can process data in a pipeline.

Here is a motivating example:

```
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
    parser.add_argument("-o","--outfile",help="Output file")
    parser.add_argument("-r","--reverse",action="store_true",help="Expand out Unicode chars")
    args = parser.parse_args(argv)

    Pipeline(args, textinfile, process, textoutfile, defaultext="_output")

if __name__ == "__main__":
    main()
```

Running this without command line options will bring up a GUI where a user may
select multiple files and output them to a directory (or default them to have
\_output appended to the filename). If all the required command line options
(infiles in this case) are given on the command line, no GUI is presented and
the app can run file -> file rather than file -> directory for the single input
file case. Likewise if the program is run with the -h command line option then
help is printed to the terminal.

Having written such an application, it is then possible, using pyinstaller, to
bundle the application as a .exe on Windows for users who do not want to install
python or use a command line. For example:

```
pyinstaller -w -F uniraw.py
```

Will result in a 30+ MB. This seems a lot, but in the modern world, it will be
barely noticeable!



