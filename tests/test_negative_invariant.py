"""Intentional CI negative test; never merge."""
import unittest
from finance.ledger import setup,receipt
import sqlite3
class DeliberateFailure(unittest.TestCase):
    def test_intentional_incorrect_ledger_expectation(self):
        db=sqlite3.connect(':memory:'); setup(db); receipt(db,'NEG',1,500)
        self.assertEqual(db.execute('SELECT SUM(debit) FROM journal').fetchone()[0],501)
        db.close()
