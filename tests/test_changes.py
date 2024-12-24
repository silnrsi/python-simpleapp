import unittest, os, io
from simpleapp import pipeline, changes

def datafile(s):
    return os.path.join(os.path.dirname(__file__), s)

def asfile(indat):
    return io.StringIO(indat)

class TestChanges(unittest.TestCase):

    def testsimple(self):
        testchanges = """
'R' > 'r'
"""
        c = changes.Changes(asfile(testchanges))
        dat = pipeline.textinfile(datafile("testin.usfm"), None)
        outdat = c.runChanges(dat)
        self.assertNotIn('R', outdat)

        

