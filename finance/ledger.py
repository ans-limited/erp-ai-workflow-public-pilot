"""Disposable SQLite accounting/inventory probe. Not production ledger."""
import sqlite3
def setup(db):
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript("""
    CREATE TABLE receipts(ext_ref TEXT UNIQUE NOT NULL, units INTEGER NOT NULL CHECK(units>0), reversed INTEGER NOT NULL DEFAULT 0);
    CREATE TABLE journal(ref TEXT NOT NULL,account TEXT NOT NULL,debit INTEGER NOT NULL DEFAULT 0,credit INTEGER NOT NULL DEFAULT 0);
    CREATE TRIGGER journal_no_update BEFORE UPDATE ON journal BEGIN SELECT RAISE(ABORT,'journal immutable'); END;
    CREATE TRIGGER journal_no_delete BEFORE DELETE ON journal BEGIN SELECT RAISE(ABORT,'journal immutable'); END;
    """)
    db.commit()
def receipt(db,ref,units,cents,*,allowed=True,period_open=True,fail=False):
    if not allowed: raise PermissionError('denied')
    if not period_open: raise ValueError('period closed')
    if units<=0 or cents<=0: raise ValueError('invalid')
    db.execute('BEGIN IMMEDIATE')
    try:
        if db.execute('SELECT 1 FROM receipts WHERE ext_ref=?',(ref,)).fetchone():
            db.commit();return False
        db.execute('INSERT INTO receipts(ext_ref,units) VALUES(?,?)',(ref,units))
        if fail: raise RuntimeError('synthetic failure')
        db.execute("INSERT INTO journal(ref,account,debit) VALUES(?,'Inventory',?)",(ref,cents))
        db.execute("INSERT INTO journal(ref,account,credit) VALUES(?,'AP',?)",(ref,cents))
        if db.execute('SELECT SUM(debit-credit) FROM journal WHERE ref=?',(ref,)).fetchone()[0]!=0:
            raise ValueError('unbalanced')
        db.commit();return True
    except Exception:
        db.rollback();raise
def reverse(db,ref):
    db.execute('BEGIN IMMEDIATE')
    try:
        row=db.execute('SELECT reversed FROM receipts WHERE ext_ref=?',(ref,)).fetchone()
        if row is None: raise LookupError(ref)
        if row[0]: db.commit();return False
        entries=list(db.execute('SELECT account,debit,credit FROM journal WHERE ref=?',(ref,)))
        for acct,debit,credit in entries:
            db.execute('INSERT INTO journal(ref,account,debit,credit) VALUES(?,?,?,?)',(ref+'-REV',acct,credit,debit))
        db.execute('UPDATE receipts SET reversed=1 WHERE ext_ref=?',(ref,))
        db.commit();return True
    except Exception: db.rollback();raise
