import unittest
from contracts.item import item_label
from consumers.card import card
class ContractTests(unittest.TestCase):
    def test_consumer(self): self.assertEqual(card("X")["label"],item_label("X"))
