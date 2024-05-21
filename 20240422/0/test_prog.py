import unittest
from unittest.mock import MagicMock
import prog


class TestMoo(unittest.TestCase):

    def test_0_moo(self):
        self.assertEqual(prog.sqroots("1 2 1"), "-1.0 -1.0")

    def test_1_moo(self):
        self.assertEqual(prog.sqroots('1 -5 6'), "3.0 2.0")

    def test_2_moo(self):
        self.assertEqual(prog.sqroots("1 -2 1"), "1.0 1.0")

    def test_exception_moo(self):
        with self.assertRaises(Exception):
            prog.sqroots("1")

class TestMooNet(unittest.TestCase):

    def setUp(self):
        self.s - MagicMock()
        self.s.sendall = lambda par: self.__dict__.setdefault("res", prog.sqroots(par))
        self.s.recv = lambda args: self.res