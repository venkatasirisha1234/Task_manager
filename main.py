from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session

app = FastAPI()
@app.get("/")
def home():
    return {"message":"Welcome to task manager"}


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


templates = Jinja2Templates(directory="templates")



DATABASE_URL = "sqlite:///./task_manager.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()



class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    completed = Column(Boolean, default=False, nullable=False)

Base.metadata.create_all(bind=engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/tasks")
def show_tasks(request: Request, db: Session = Depends(get_db)):
    tasks = db.query(Task).order_by(Task.id.desc()).all()

    return templates.TemplateResponse(
        "tasks.html",
        {
            "request": request,
            "tasks": tasks
        }
    )



@app.post("/tasks")
def add_task(
    title: str = Form(...),
    db: Session = Depends(get_db)
):
    new_task = Task(title=title)

    db.add(new_task)
    db.commit()

    return RedirectResponse(
        url="/tasks",
        status_code=303
    )



@app.post("/tasks/{task_id}/complete")
def complete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is not None:
        task.completed = True
        db.commit()

    return RedirectResponse(
        url="/tasks",
        status_code=303
    )



@app.post("/tasks/{task_id}/delete")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is not None:
        db.delete(task)
        db.commit()

    return RedirectResponse(
        url="/tasks",
        status_code=303
    )