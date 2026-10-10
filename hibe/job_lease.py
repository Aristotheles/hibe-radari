"""Expiring ownership for result publication in the existing records store."""
import json
import threading
import time
import uuid
from contextlib import contextmanager

_guard=threading.RLock()

def _update(store,ident,owner,acquire,ttl):
    def updated(old):
        old=old or {}
        if acquire:
            if old.get('expires_at',0)>time.time():return None
            return {'id':ident,'owner':owner,'expires_at':time.time()+ttl}
        if old.get('owner')!=owner:return None
        return {'id':ident,'expires_at':0}
    db=getattr(store,'db',None)
    if hasattr(db,'collection'):
        from google.cloud import firestore
        ref=db.collection('job_leases').document(ident)
        @firestore.transactional
        def mutate(transaction):
            new=updated(ref.get(transaction=transaction).to_dict())
            if new is None:return False
            transaction.set(ref,new);return True
        return mutate(db.transaction())
    if hasattr(db,'execute'):
        with store.lock:
            db.execute('BEGIN IMMEDIATE')
            try:
                row=db.execute('SELECT value FROM records WHERE kind=? AND id=?',('job_leases',ident)).fetchone()
                new=updated(json.loads(row[0]) if row else None)
                if new is not None:db.execute('INSERT OR REPLACE INTO records VALUES(?,?,?)',('job_leases',ident,json.dumps(new)))
                db.commit();return new is not None
            except Exception:
                db.rollback();raise
    with _guard:
        new=updated(store.get('job_leases',ident))
        if new is None:return False
        store.put('job_leases',ident,new);return True

@contextmanager
def processing_lease(store,ident,ttl=900):
    owner=uuid.uuid4().hex
    acquired=_update(store,ident,owner,True,ttl)
    try:yield owner if acquired else None
    finally:
        if acquired:_update(store,ident,owner,False,ttl)

def owns_lease(store,ident,owner):
    current=store.get('job_leases',ident) or {}
    return bool(owner and current.get('owner')==owner and current.get('expires_at',0)>time.time())
