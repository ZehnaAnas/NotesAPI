from fastapi import FastAPI,Depends,APIRouter
from typing import Annotated
import uvicorn
from sqlmodel import Session,select
from database import create_db_tables,get_session,Note
import redis
from Redis.cache import RedisCache
from Redis.primary import MockPrimaryStore
import json
from celery_app import celery_app
from celery.result import AsyncResult
from tasks import generate_digest

router = APIRouter()

r = redis.Redis(host='redis', port=6379,decode_responses=True)
primary = MockPrimaryStore(read_latency_ms=60)
cache = RedisCache(redis_client=r,ttl=30)

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(title="Notes API")

@app.get("/")
def hello():
    count = r.incr("hits")
    return f"Hello from Docker! I have been seen {count} time(s).\n"

@app.on_event("startup")
def on_startup():
    create_db_tables()
    
@app.post("/notes")
def create_notes(note:Note,session:SessionDep):
    session.add(note)
    session.commit()
    session.refresh(note)
    cache.invalidate("all")
    r.set(f"note:{note.note_id}", json.dumps({"note_id": note.note_id, "note": note.note}))
    return note

@app.get("/notes")
def get_notes(session:SessionDep):
    def load_notes(_:str):
        notes = session.exec(select(Note)).all()
        return {"notes":json.dumps(
            [note.model_dump(mode="json")
            for note in notes]
        )
    }
    result, hit, latency = cache.get("all",load_notes)
    if hit:
        print("cache hit")
    else:
        print("cache miss")
    return json.loads(result["notes"])

@app.get("/notes/{note_id}")
def get_one_note(note_id:int,session:SessionDep):
    note = session.get(Note,note_id)
    return note

@router.post("/notes/digest")
def trigger_digest():
    task = generate_digest.delay()
    return {"task_id":task.id}

@router.get("/notes/digest/{task_id}")
def get_digest_status(task_id:str):
    result = AsyncResult(task_id, app=celery_app)
    if result.state == "PENDING":
        return {"status":"pending"}
    elif result.state == "SUCCESS":
        return {"status":"success","result":result.result}
    elif result.state == "FAILURE":
        return {"status":"failed","error":str(result.result)}
    else:
        return {"status":result.state}
    
@app.put("/notes/{note_id}")
def update_note(note_id:int,session:SessionDep,n:Note):
    notes = session.get(Note,note_id)
    notes.note = n.note
    session.commit()
    session.refresh(notes)
    cache.invalidate("all")
    return notes

@app.delete("/notes/{note_id}")
def delete_note(note_id:int,session: SessionDep):
    note = session.get(Note,note_id)
    session.delete(note)
    session.commit()
    cache.invalidate("all")
    return {"ok":True}


if __name__ == "__main__":
    uvicorn.run(app=app,host="localhost",port=8000)






