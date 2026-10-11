import unittest
from verified import *
class TestVerified(unittest.TestCase):
 def test_equivalent(self):
  a='GPU is faster than CPU';b='GPU faster than CPU';p=witness(a,b)
  self.assertIsNotNone(p);self.assertEqual(verify(a,b,p),'accept')
 def test_direction(self):
  a='GPU faster than CPU';b='CPU faster than GPU';self.assertIsNone(witness(a,b))
 def test_tamper(self):
  a='GPU faster than CPU';p=witness(a,a);p['left']='0'*64
  self.assertEqual(verify(a,a,p),'reject')
 def test_unknown(self):self.assertIsNone(witness('A complicated paragraph','Another paragraph'))
 def test_merkle(self):
  self.assertEqual(merkle(['GPU faster than CPU']),merkle(['GPU is faster than CPU']))
  self.assertNotEqual(merkle(['GPU faster than CPU']),merkle(['CPU faster than GPU']))
 def test_index(self):
  s=IndexedStore();s.add('GPU faster than CPU');s.add('CPU faster than GPU')
  self.assertTrue(s.query('GPU is faster than CPU')[0]['canonical_match'])
 def test_persistence(self):
  import tempfile,os
  with tempfile.TemporaryDirectory() as d:
   path=os.path.join(d,'db');IndexedStore(path).add('GPU faster than CPU')
   self.assertTrue(IndexedStore(path).query('GPU faster than CPU'))
if __name__=='__main__':unittest.main()
