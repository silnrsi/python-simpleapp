import re
import regex
import logging

logger = logging.getLogger(__name__)

class Changes:

    errorfn = print

    def __init__(self, cfile):
        if hasattr(cfile, 'read'):
            inf = cfile
            cfile = None
        else:
            inf = open(cfile, encoding="utf-8")
        alllines = list(inf.readlines())
        self.changes = self.readChanges(alllines, fname=cfile)
        inf.close()

    def make_contextsfn(self, bk, *changes):
        # functional programmers eat your hearts out
        def makefn(reg, currfn):
            if currfn is not None:
                def compfn(fn, b, s):
                    def domatch(m):
                        return currfn(lambda x:fn(m.group(0)), b, m.group(0))
                    return reg.sub(domatch, s) if bk is None or b == bk else s
            else:
                def compfn(fn, b, s):
                    return reg.sub(lambda m:fn(m.group(0)), s) if bk is None or b == bk else s
            return compfn
        return reduce(lambda currfn, are: makefn(are, currfn), reversed([c for c in changes if c is not None]), None)

    def readChanges(self, lines, passes=None, fname=None):
        changes = {}
        if passes is None:
            passes = ["default"]
        qreg = r'(?:"((?:[^"\\]|\\.)*?)"|' + r"'((?:[^'\\]|\\.)*?)')"
        i = 0
        while i < len(lines):
            l = lines[i].strip().replace(u"\uFEFF", "")
            i += 1
            while l.endswith("\\") and i < len(lines):
                l = l[:-1] + lines[i].strip()
                i += 1
            l = re.sub(r"\s*#.*$", "", l)
            if not len(l):
                continue
            contexts = []
            atcontexts = []
            m = re.match(r"^\s*sections\s*\((.*?)\)", l)
            if m:
                ts = m.group(1).split(",")
                passes = [t.strip()[1:-1].strip() for t in ts]
                for p in passes:
                    if p not in changes:
                        changes[p] = []
                continue
            m = re.match(r"^\s*include\s+(['\"])(.*?)\1", l)
            if m:
                lchs = self.readChanges(os.path.join(os.path.dirname(fname), m.group(2)), passes=passes)
                for k, v in lchs.items():
                    changes.setdefault(k, []).extend(v)
                continue
            # test for "at" command
            m = re.match(r"^\s*at\s+(.*?)\s+(?=in|['\"])", l)
            if m:
                atref = RefList.fromStr(m.group(1), context=AnyBooks)
                for r in atref.allrefs():
                    if r.chap == 0:
                        atcontexts.append((r.book, None))
                    elif r.verse == 0:
                        atcontexts.append((r.book, regex.compile(r"(?<=\\c {}\D).*?(?=$|\\[cv]\s)".format(r.chap), flags=regex.S)))
                    else:
                        if r.first != r.last:
                            outv = "{}{}-{}{}".format(r.first.verse, r.first.subverse or "", r.last.verse, r.last.subverse or "")
                        else:
                            outv = '{}{}'.format(r.verse, r.subverse or "")
                        atcontexts.append((r.book, regex.compile(r"\\c {}\D(?:[^\\]|\\(?!c\s))*?\K\\v {}\D.*?(?=$|\\[cv]\s)".format(r.chap, outv), flags=regex.S|regex.V1)))
                l = l[m.end():].strip()
            else:
                atcontexts = [None]
            # test for 1+ "in" commands
            while True:
                m = re.match(r"^\s*in\s+"+qreg+r"\s*:\s*", l)
                if not m:
                    break
                try:
                    contexts.append(regex.compile(m.group(1) or m.group(2), flags=regex.M))
                except re.error as e:
                    self.printer.doError("Regular expression error: {} in changes file at line {}".format(str(e), i+1),
                                         show=not self.printer.get("c_quickRun"))
                    break
                l = l[m.end():].strip()
            # capture the actual change
            m = re.match(r"^"+qreg+r"\s*>\s*"+qreg, l)
            if m:
                try:
                    r = regex.compile(m.group(1) or m.group(2), flags=regex.M)
                    # t = regex.template(m.group(3) or m.group(4) or "")
                except (re.error, regex._regex_core.error) as e:
                    self.printer.doError("Regular expression error: {} in changes file at line {}".format(str(e), i+1))
                    continue
                for at in atcontexts:
                    if at is None:
                        context = self.make_contextsfn(None, *contexts) if len(contexts) else None
                    elif len(contexts) or at[1] is not None:
                        context = self.make_contextsfn(at[0], at[1], *contexts)
                    else:
                        context = at[0]
                    ch = (context, r, m.group(3) or m.group(4) or "", f"{fname} line {i+1}")
                    for p in passes:
                        changes.setdefault(p, []).append(ch)
                    logger.log(7, f"{context=} {r=} {m.groups()=}")
                continue
            elif len(l):
                logger.warning(f"Faulty change line found in {fname} at line {i}:\n{l}")
        return changes

    def runChanges(self, dat, bk=None, category=None):
        if category is None:
            category = "default"
        changes = self.changes.get(category, [])
        def wrap(t, l):
            def proc(m):
                res = m.expand(t) if isinstance(t, str) else t(m)
                logger.log(5, "match({0},{1})={2}->{3} at {4}".format(m.start(), m.end(), m.string[m.start():m.end()], res, l))
                return res
            return proc
        for c in changes:
            if bk is not None:
                logger.debug("at {} Change: {}".format(bk, c))
            try:
                if c[0] is None:
                    dat = c[1].sub(wrap(c[2], c[3]), dat)
                elif isinstance(c[0], str):
                    if c[0] == bk:
                        dat = c[1].sub(wrap(c[2], c[3]), dat)
                else:
                    def simple(s):
                        return c[1].sub(wrap(c[2], c[3]), s)
                    dat = c[0](simple, bk, dat)
            except TypeError as e:
                raise TypeError(str(e) + "\n at "+c[3])
            except regex._regex_core.error as e:
                if self.errorfn is not None:
                    self.errorfn(str(e) + "\n at " + c[3])
        return dat


