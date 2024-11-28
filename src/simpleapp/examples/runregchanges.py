#!/usr/bin/python3

import os, regex, sys
import logging
import simpleapp

try:
    from simpleapp.pipeline import Pipeline, textinfile, textoutfile
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
    from simpleapp.pipeline import Pipeline, textinfile, textoutfile

logger = logging.getLogger(__name__)

def runChanges(changes, dat, errorfn=None):
    def wrap(t, l):
        def proc(m):
            res = m.expand(t) if isinstance(t, str) else t(m)
            logger.log(5, "match({0},{1})={2}->{3} at {4}".format(m.start(), m.end(), m.string[m.start():m.end()], res, l))
            return res
        return proc
    for c in changes:
        try:
            if c[0] is None:
                dat = c[1].sub(wrap(c[2], c[3]), dat)
            elif isinstance(c[0], str):
                dat = c[1].sub(wrap(c[2], c[3]), dat)
            else:
                def simple(s):
                    return c[1].sub(wrap(c[2], c[3]), s)
                dat = c[0](simple, dat)
        except TypeError as e:
            raise TypeError(str(e) + "\n at "+c[3])
        except regex._regex_core.error as e:
            if errorfn is not None:
                errorfn(str(e) + "\n at " + c[3])
    return dat

def _make_contextsfn(*changes):
    # functional programmers eat your hearts out
    def makefn(reg, currfn):
        if currfn is not None:
            def compfn(fn, b, s):
                def domatch(m):
                    return currfn(lambda x:fn(m.group(0)), b, m.group(0))
                return reg.sub(domatch, s)
        else:
            def compfn(fn, b, s):
                return reg.sub(lambda m:fn(m.group(0)), s)
        return compfn
    return reduce(lambda currfn, are: makefn(are, currfn), reversed([c for c in changes if c is not None]), None)

def readChanges(fname):
    changes = []
    if not os.path.exists(fname):
        return []
    qreg = r'(?:"((?:[^"\\]|\\.)*?)"|' + r"'((?:[^'\\]|\\.)*?)')"
    with open(fname, encoding="utf-8") as inf:
        alllines = list(inf.readlines())
        i = 0
        while i < len(alllines):
            l = alllines[i].strip().replace(u"\uFEFF", "")
            i += 1
            while l.endswith("\\") and i < len(alllines):
                l = l[:-1] + alllines[i].strip()
                i += 1
            l = re.sub(r"\s*#.*$", "", l)
            if not len(l):
                continue
            contexts = []
            atcontexts = []
            m = re.match(r"^\s*include\s+(['\"])(.*?)\1", l)
            if m:
                changes.extend(readChanges(os.path.join(os.path.dirname(fname), m.group(2))))
                continue
            # test for 1+ "in" commands
            while True:
                m = re.match(r"^\s*in\s+"+qreg+r"\s*:\s*", l)
                if not m:
                    break
                try:
                    contexts.append(regex.compile(m.group(1) or m.group(2), flags=regex.M))
                except re.error as e:
                    print("Regular expression error: {} in changes file at line {}".format(str(e), i+1))
                    break
                l = l[m.end():].strip()
            # capture the actual change
            m = re.match(r"^"+qreg+r"\s*>\s*"+qreg, l)
            if m:
                try:
                    r = regex.compile(m.group(1) or m.group(2), flags=regex.M)
                    # t = regex.template(m.group(3) or m.group(4) or "")
                except (re.error, regex._regex_core.error) as e:
                    print("Regular expression error: {} in changes file at line {}".format(str(e), i+1))
                    continue
                context = make_contextsfn(None, *contexts) if len(contexts) else None
                changes.append((context, r, m.group(3) or m.group(4) or "", f"{fname} line {i+1}"))
                continue
            elif len(l):
                logger.warning(f"Faulty change line found in {fname} at line {i}:\n{l}")
    return changes

def main(argv=None):
    parser = simpleapp.ArgumentParser(prog='runregchanges')
    parser.add_argument("infiles",nargs="+",help="Input file")
    parser.add_argument("-c","--changes",required=True,help="changes.txt")
    parser.add_argument("-o","--outfile",help="Output file")
    parser.add_argument('-l','--logging',help="Logging level [DEBUG, INFO, WARN, ERROR, number]")
    parser.add_argument('--logfile',default='runregchanges.log',help='Set logging file')
    args = parser.parse_args(argv)

    changes = readChanges(args.changes)
    args.changeactions = changes
    Pipeline(args.infiles, args.outfile, args, textinfile, runChanges, textoutfile,
            logging=True, defaultext="_changed")

if __name__ == "__main__":
    main()
