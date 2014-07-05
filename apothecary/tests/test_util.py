"""
"""

import unittest
    
import apothecary.util



class TestUtil(unittest.TestCase):
    """
    """
    def test_hash(self):
        dig = apothecary.util.hash('mine'.encode())
        self.assertEqual(len(dig), 64)
        dig = apothecary.util.hash('minessssss'.encode())
        self.assertEqual(len(dig), 64)

    def test_benc(self):
        l = 'minesesasdasdasdasdasd'.encode()
        enc = apothecary.util.benc.encode(l)
        size = apothecary.util.benc.overhead(len(l))
        self.assertLessEqual(len(enc), size)
        self.assertEqual(apothecary.util.benc.decode(enc), l)

    def test_time(self):
        t = apothecary.util.time()
        self.assertIsInstance(t, int)
        self.assertGreater(t, 1403818900)

    def test_random(self):
        r = apothecary.util.random.read(16)
        self.assertEqual(len(r), 16)

    def test_token(self):
        t = apothecary.util.token(16)
        self.assertEqual(len(t), 16)