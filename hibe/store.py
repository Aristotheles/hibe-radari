import sqlite3,json,threading
class MemoryStore:
 def __init__(self):self.data={}
 def get(self,k,i):return json.loads(json.dumps(self.data.get((k,i))))
 def put(self,k,i,v):self.data[k,i]=json.loads(json.dumps(v))
 def all(self,k):return [json.loads(json.dumps(v)) for (kind,_),v in self.data.items() if kind==k]
class SQLiteStore:
 def __init__(self,path):
  self.db=sqlite3.connect(path,check_same_thread=False);self.lock=threading.RLock()
  self.db.execute('CREATE TABLE IF NOT EXISTS records(kind TEXT,id TEXT,value TEXT,PRIMARY KEY(kind,id))');self.db.commit()
 def get(self,k,i):
  with self.lock:
   r=self.db.execute('SELECT value FROM records WHERE kind=? AND id=?',(k,i)).fetchone();return json.loads(r[0]) if r else None
 def put(self,k,i,v):
  with self.lock:self.db.execute('INSERT OR REPLACE INTO records VALUES(?,?,?)',(k,i,json.dumps(v)));self.db.commit()
 def all(self,k):
  with self.lock:return [json.loads(r[0]) for r in self.db.execute('SELECT value FROM records WHERE kind=?',(k,))]
class FirestoreStore:
 def __init__(self):
  from firebase_admin import firestore
  self.db=firestore.client()
 def get(self,k,i):return self.db.collection(k).document(i).get().to_dict()
 def put(self,k,i,v):self.db.collection(k).document(i).set(v)
 def all(self,k):return [d.to_dict() for d in self.db.collection(k).stream()]
