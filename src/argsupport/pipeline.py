
from glob import glob
import os, sys, logging

class Pipeline:
    def __init__(self, infiles, outfile, args, *fns, **kw):
        ''' Process possibly multiple input files to an output file or directory with
            given command line args. The output of one fn is fed as the first parameter
            to the next fn, with args as the second parameter. The final function is
            called with: data, outfile, args.
            kw may take the following options:
                logging:          if not None, enables logging based on --logging, --logfile
                multiprocessing:  if true processes files in parallel based on --jobs
        '''
        self.args = args
        self.fns = fns
        self.kw = kw
        self.infiles = infiles
        self.outfile = outfile
        if kw.get('logging', None):
            self.setup_logging(kw['logging'], args)
        self.procargs()

    def procargs(self):
        infiles = [glob(f) for f in self.infiles]
        if len(infiles) > 1:
            single = False
            # can raise FileExistsError if a file exists
            self.outfile = self.outfile or self.kw.get("defaultext", None)
            if self.outfile is not None:
                os.makedirs(self.outfile, exist_ok=True)
        else:
            single = True
            if not self.outfile and 'defaultext' not in self.kw:
                self.outfile = None
            else:
                outname = self.outfile or infiles[0] + self.kw.get("defaulttext", "")
                if outname == infiles[0]:
                    raise ValueError("Can't overwrite input file")
                elif os.path.isdir(outname):
                    self.outfile = os.path.join(outname, infiles[0])
                else:
                    self.outfile = outname

        if 'multiprocessing' in kw:
            jobs = int(getattr(self.args, 'jobs', 0))
        else:
            jobs = 1

        if jobs == 1 or single:
            for inf in infiles:
                self._procfile(inf, single=single)
        else:
            pool = Pool(processes=jobs)
            results = list(pool.map_async(self._procfile, infiles).get())
            pool.close()
            pool.join()

    def _calcoutput(self, inf, single=False):
        if self.outfile is None and 'defaultext' not in self.kw:
            return None
        if single:
            if self.outfile is not None:
                return self.outfile
        elif self.outfile is not None:
            return os.path.join(self.outfile, os.path.basename(inf))
        return inf + kw['defaultext']

    def _procfile(self, inf, single=False):
            currval = inf
            final = -1
            outf = self._calcoutput(inf, single=single)
            if outf is None:
                final = len(fns)
                
            for fn in fns[:final]:
                currval = fn(currval, self.args)
            if final < 0:
                fns[-1](currval, outf, self.args)

    def setup_logging(self, logging, args):
        if args.logging:
            try:
                loglevel = int(args.logging)
            except ValueError:
                loglevel = getattr(logging, args.logging.upper(), None)
            if isinstance(loglevel, int):
                parms = {'level': loglevel, 'datefmt': '%d/%b/%Y %H:%M:%S', 'format': '%(asctime)s.%(msecs)03d %(levelname)s:%(module)s(%(lineno)d) %(message)s'}
                if args.logfile.lower() != "none":
                    logfh = open(args.logfile, "w", encoding="utf-8")
                    parms.update(stream=logfh, filemode="w") #, encoding="utf-8")
                try:
                    logging.basicConfig(**parms)
                except FileNotFoundError as e:      # no write access to the log
                    print("Exception", e)


def textinfile(fname, args, encoding=None):
    if encoding is None:
        encoding = "utf-8"
    with open(fname, encoding=encoding) as inf:
        res = inf.read()
    return res

def textoutfile(txt, fname, args, encoding=None):
    if encoding is None:
        encoding = "utf-8"
    with open(fname, "w", encoding=encoding) as outf:
        outf.write(txt)

def jsoninfile(fname, args, encoding=None):
    if encoding is None:
        encoding = "utf-8"
    with open(fname, encoding=encoding) as inf:
        res = json.load(inf)
    return res
    
def jsonoutfile(dat, fname, args, encoding=None, indent=-1, sort_keys=False):
    ''' outputs the data as a json file '''
    if encoding is None:
        encoding = "utf-8"
    with open(fname, "w", encoding=encoding) as outf:
        json.dump(dat, outf, ensure_ascii=False, indent=indent, sort_keys=sort_keys)

