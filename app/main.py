from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from prometheus_fastapi_instrumentator import Instrumentator

from app.database import Base, engine, get_db
from app import models, schemas

app = FastAPI(title="TaskVault", version="0.1.0")

# Chapter 1: create tables on startup. Fine for learning; a real system
# would use Alembic migrations instead.
Base.metadata.create_all(bind=engine)

# Chapter 3: instrument(app) attaches middleware that times/counts every
# request as it flows through. expose(app) adds the GET /metrics route
# that renders those counters in Prometheus's text format.
Instrumentator().instrument(app).expose(app)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    """Liveness/readiness probe target — Kubernetes will call this in Chapter 4."""
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.post("/items", response_model=schemas.TaskOut, status_code=201)
def create_item(item: schemas.TaskCreate, db: Session = Depends(get_db)):
    task = models.Task(title=item.title, description=item.description)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/items", response_model=list[schemas.TaskOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(models.Task).order_by(models.Task.id).all()


@app.get("/items/{item_id}", response_model=schemas.TaskOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).get(item_id)
    if not task:
        raise HTTPException(status_code=404, detail="item not found")
    return task


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).get(item_id)
    if not task:
        raise HTTPException(status_code=404, detail="item not found")
    db.delete(task)
    db.commit()
