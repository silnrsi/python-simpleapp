import unittest, os, io
from argsupport import pipeline

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

if __name__ == "__main__":
    unittest.main()
