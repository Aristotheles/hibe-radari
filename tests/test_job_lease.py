import unittest,tempfile
from pathlib import Path
from hibe.store import MemoryStore,SQLiteStore
from hibe.job_lease import processing_lease

class JobLeaseTests(unittest.TestCase):
 def verify(self,store):
  with processing_lease(store,'result') as first:
   self.assertTrue(first)
   with processing_lease(store,'result') as second:self.assertFalse(second)
  with self.assertRaises(RuntimeError):
   with processing_lease(store,'result') as acquired:
    self.assertTrue(acquired);raise RuntimeError('Interrupted publication')
  with processing_lease(store,'result') as acquired:self.assertTrue(acquired)
  store.put('job_leases','result',{'expires_at':0,'owner':'old'})
  with processing_lease(store,'result') as acquired:self.assertTrue(acquired)
 def test_memory_single_owner_expiry_and_failure_release(self):self.verify(MemoryStore())
 def test_sqlite_lease_is_atomic_across_store_connections(self):
  with tempfile.TemporaryDirectory() as root:
   first=SQLiteStore(Path(root)/'test.db');second=SQLiteStore(Path(root)/'test.db')
   try:
    self.verify(first)
    with processing_lease(first,'result') as a:
     self.assertTrue(a)
     with processing_lease(second,'result') as b:self.assertFalse(b)
   finally:first.db.close();second.db.close()
