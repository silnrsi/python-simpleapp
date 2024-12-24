import unittest, os, io
from simpleapp import pipeline

def datafile(s):
    return os.path.join(os.path.dirname(__file__), s)

class TestPipeline(unittest.TestCase):

    def test_textin(self):
        dat = pipeline.textinfile(datafile("testin.usfm"), None)
        self.assertEqual(dat[:10], r"\id RUT - ")

    def test_textout(self):
        teststr = "This is a test\n"
        of = io.StringIO()
        pipeline.textoutfile(teststr, of, None)
        self.assertEqual(of.getvalue(), teststr)
        of.close()

    @unittest.skip
    def test_usfmin(self):
        dat = pipeline.usfminfile(datafile("testin.usfm"), None)
        val = dat.getroot().find('.//para[@style="p"]/verse').tail[21:27]
        self.assertEqual(val, "judges")

    @unittest.skip
    def test_csvout(self):
        dat = pipeline.usfminfile(datafile("testin.usfm"), None)
        res = []
        row = []
        for v in dat.getroot().findall('.//para[@style="p"]/verse'):
            n = v.get('number')
            if n == "1":
                if len(row):
                    res.append(row)
                    row = []
            if 'Naomi' in v.tail:
                row.append(v.get('number'))
        if len(row):
            res.append(row)
        of = io.StringIO()
        pipeline.csvoutfile(res, of, None)
        csvdat = of.getvalue().split("\r\n")
        self.assertEqual(len(csvdat), 5)
        self.assertEqual(csvdat[1], "1,2,6,18,20,22")

    def test_csvdictin(self):
        indat = "word,num\nhello,3\ngoodbye,1"
        fields = []
        inf = io.StringIO(indat)
        dat = pipeline.csvinfiledict(inf, None, fields=fields)
        inf.close()
        self.assertEqual(len(dat), 2)
        self.assertEqual(dat[0]['word'], "hello")
        self.assertEqual(len(fields), 2)
        self.assertEqual(fields[1], "num")

    def test_csvin(self):
        indat = "word,num\nhello,3\ngoodbye,1"
        fields = []
        inf = io.StringIO(indat)
        dat = pipeline.csvinfile(inf, None)
        self.assertEqual(len(dat), 3)
        self.assertEqual(dat[1][0], "hello")

    def test_jsonin(self):
        dat = pipeline.jsoninfile(datafile("testin.json"), None)
        self.assertEqual(dat['content'][9]['content'][1][21:27], "judges")

    def test_jsonout(self):
        indat = "word,num\nhello,3\ngoodbye,1"
        fields = []
        inf = io.StringIO(indat)
        dat = pipeline.csvinfiledict(inf, None, fields=fields)
        inf.close()
        of = io.StringIO()
        pipeline.jsonoutfile(dat, of, None)
        jsdat = of.getvalue()
        of.close()
        self.assertEqual(jsdat, '[\n{\n"word": "hello",\n"num": "3"\n},\n{\n"word": "goodbye",\n"num": "1"\n}\n]')


if __name__ == "__main__":
    unittest.main()
