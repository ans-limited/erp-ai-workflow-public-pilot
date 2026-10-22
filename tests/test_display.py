import unittest
from catalog.display import label
class DisplayTests(unittest.TestCase):
    def test_label(self): self.assertEqual(label("X"),"Item X")
