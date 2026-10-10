import unittest,tempfile,os
from meaninghash import *
class Test(unittest.TestCase):
 def test_deterministic(self):self.assertEqual(sketch('GPU faster than CPU'),sketch('GPU faster than CPU'))
 def test_canonical(self):self.assertEqual(identity('GPU is faster than CPU'),identity('gpu faster than cpu'))
 def test_direction(self):self.assertNotEqual(identity('GPU faster than CPU'),identity('CPU faster than GPU'))
 def test_negation(self):self.assertNotEqual(identity('gpu uses cuda'),identity('gpu does not use cuda'))
 def test_distance(self):self.assertEqual(distance(sketch('a'),sketch('a')),0)
 def test_index(self):
  with tempfile.TemporaryDirectory() as d:
   ix=Index(os.path.join(d,'x.db'));ix.add('GPU faster than CPU');ix.add('CPU faster than GPU')
   self.assertEqual(ix.query('GPU is faster than CPU')[0]['text'],'GPU faster than CPU')
if __name__=='__main__':unittest.main()
