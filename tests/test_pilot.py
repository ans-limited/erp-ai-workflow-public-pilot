import unittest,sqlite3
from finance.ledger import setup,receipt,reverse
from hosted.ci_policy import ast_same
class PilotTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:');setup(self.db)
    def tearDown(self):self.db.close()
    def test_post_balances(self):
        receipt(self.db,'A',2,500)
        self.assertEqual(self.db.execute('SELECT SUM(debit-credit) FROM journal').fetchone()[0],0)
    def test_duplicate_prevented(self):
        receipt(self.db,'A',2,500)
        self.assertFalse(receipt(self.db,'A',2,500))
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM journal').fetchone()[0],2)
    def test_denial(self):
        with self.assertRaises(PermissionError):receipt(self.db,'A',2,500,allowed=False)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0],0)
    def test_period_lock(self):
        with self.assertRaises(ValueError):receipt(self.db,'A',2,500,period_open=False)
    def test_atomic_rollback(self):
        with self.assertRaises(RuntimeError):receipt(self.db,'A',2,500,fail=True)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0],0)
    def test_reversal(self):
        receipt(self.db,'A',2,500)
        self.assertTrue(reverse(self.db,'A'))
        self.assertFalse(reverse(self.db,'A'))
        self.assertEqual(self.db.execute('SELECT SUM(debit-credit) FROM journal').fetchone()[0],0)
    def test_immutable(self):
        receipt(self.db,'A',2,500)
        with self.assertRaises(sqlite3.IntegrityError):self.db.execute('DELETE FROM journal')
    def test_ast_comment(self):self.assertTrue(ast_same('x=1','x=1\n# hi'))
    def test_ast_change(self):self.assertFalse(ast_same('x=1','x=2'))
if __name__=='__main__':unittest.main()
