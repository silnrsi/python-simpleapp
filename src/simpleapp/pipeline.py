
from glob import glob
import os, sys, logging, json, csv
from contextlib import contextmanager

class Pipeline:
    def __init__(self, args, *fns, **kw):
        ''' Process possibly multiple input files to an output file or directory with
            given command line args. The output of one fn is fed as the first parameter
            to the next fn, with args as the second parameter. The final function is
            called with: data, outfile, args.
            kw may take the following options:
                multiprocessing:  if true processes files in parallel based on --jobs
        '''
        self.args = args
        self.fns = fns
        self.kw = kw
        infiles = kw.get('infiles', getattr(args, 'infile', getattr(args, 'infiles', None)))
        if infiles is None:
            self.infiles = None
        else:
            infiles = [infiles] if isinstance(infiles, str) else infiles
            self.infiles = sum([glob(f) for f in infiles], []) if infiles is not None else None
        self.outfile = getattr(args, 'outfile', getattr(args, 'outfiles', getattr(args, 'outdir', None)))
        self.outfilefn = self.make_outfilefn()
        self.procargs()

    def make_outfilefn(self):
        if '*' in self.outfile:
            template = self.outfile.replace("*", "{}")
            if '.' in self.outfile:
                def dofn(infile):
                    return template.format(os.path.splitext(os.path.basename(infile))[0])
            else:
                def dofn(infile):
                    bits = os.path.splitext(os.path.basename(infile))
                    return template.format(bits[0]) + bits[1]
        elif os.path.isdir(self.outfile):
            def dofn(infile):
                return os.path.join(self.outfile, os.path.basename(infile))
        elif len(self.infiles) < 2:
            def dofn(infile):
                return self.outfile
        else:
            raise ValueError("Pipeline cannot convert multiple input files {} into a single output file {}".format(self.infiles, self.outfile))
        return dofn

    def procargs(self):
        if 'multiprocessing' in self.kw and self.infiles is not None and len(self.infiles) > 1:
            jobs = int(getattr(self.args, 'jobs', 0))
        else:
            jobs = 1

        if jobs == 1 or single:
            for inf in self.infiles:
                self._procfile(inf)
        else:
            pool = Pool(processes=jobs)
            results = list(pool.map_async(self._procfile, infiles).get())
            pool.close()
            pool.join()

    def _procfile(self, inf):
            currval = inf
            final = -1
            outf = None if inf is None else self.outfilefn(inf)
            if outf is None:
                final = len(self.fns)
                
            for fn in self.fns[:final]:
                currval = fn(currval, self.args)
            if final < 0:
                self.fns[-1](currval, outf, self.args)

@contextmanager
def _opener(fname, *args, encoding=None):
    if encoding is None:
        encoding = "utf-8"
    inout = args[0] if len(args) else "r"
    res = None
    try:
        if ("r" in inout and hasattr(fname, "read")) \
                or ("w" in inout and hasattr(fname, "write")):
            yield fname
        else:
            res = open(fname, inout, encoding=encoding)
            yield res
    finally:
        if res is not None:
            res.close()


def f_(fn, *args, **kw):
    def wrapped(*a, **k):
        nk = dict(list(k.items()) + list(kw.items()))
        return fn(*(a + args), **nk)
    return wrapped

def textinfile(fname, args, encoding=None):
    with _opener(fname, encoding=encoding) as inf:
        res = inf.read()
    return res

def textoutfile(txt, fname, args, encoding=None):
    with _opener(fname, "w", encoding=encoding) as outf:
        outf.write(txt)

def jsoninfile(fname, args, encoding=None):
    with _opener(fname, encoding=encoding) as inf:
        res = json.load(inf)
    return res
    
def jsonoutfile(dat, fname, args, encoding=None, indent=-1, sort_keys=False):
    ''' outputs the data as a json file '''
    with _opener(fname, "w", encoding=encoding) as outf:
        json.dump(dat, outf, ensure_ascii=False, indent=indent, sort_keys=sort_keys)

def csvinfile(fname, args, encoding=None):
    with _opener(fname, encoding=encoding) as inf:
        reader = csv.reader(inf)
        data = [row for row in reader]
    return data

def csvinfiledict(fname, args, encoding=None, fields=None):
    fieldnames = None
    if fields is not None and len(fields):
        fieldnames = fields
    with _opener(fname, encoding=encoding) as inf:
        reader = csv.DictReader(inf, fieldnames)
        data = [row for row in reader]
        if fields is not None:
            fields[:] = reader.fieldnames
    return data

def csvoutfile(dat, fname, args, encoding=None, fields=None, noheader=False, sortby=None):
    if not len(dat):
        return None
    settings = {}
    if isinstance(fname, str) and fname.lower().endswith(".tsv"):
        settings = dict(delimiter="\t", lineterminator="\n")
    if sortby is not None:
        if sortby is True:
            data.sort()
        else:
            dat.sort(key=sortby)
    with _opener(fname, "w", encoding=encoding) as outf:
        if hasattr(dat[0], 'items'):
            writer = csv.DictWriter(outf, fields, **settings)
            if not noheader:
                writer.writeheader()
            for r in dat:
                outr = {k:r[k] for k in fields}
                writer.writerow(outr)
        else:
            writer = csv.writer(outf, **settings)
            writer.writerows(dat)
    return None

