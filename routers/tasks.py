from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models.models import todo_tasks

router = APIRouter()

class AddTask(BaseModel):
    user_id: str
    task_description: str
    is_completed: bool = False

class Tasks:
    def __init__(self, db:Session):
        self.db = db

    def get_all_tasks(self, user_id: str):
        try:
            tasks = self.db.query(todo_tasks).filter(todo_tasks.user_id == user_id).all()
            return tasks
        except Exception as e:
            print(e)
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                content={"message": "Internal Server Error"})
    
    def add_task(self, details:AddTask):
        try:
            task_details = todo_tasks(
                user_id=details.user_id,
                task_description=details.task_description,
                is_completed=details.is_completed
            )

            self.db.add(task_details)
            self.db.commit()
            self.db.close()

            return JSONResponse(status_code=status.HTTP_201_CREATED, 
                                content={"message": "Task created successfully"})
        except Exception as e:
            self.db.close()
            print(e)
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                content={"message": "Internal Server Error"})
        
    def update_task(self, task_id: str):
        try:
            task = self.db.query(todo_tasks).filter(todo_tasks.id == task_id).first()
            if not task:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, 
                                    content={"message": "Task not found"})
            
            task.is_completed = True
            self.db.commit()
            self.db.close()

            return JSONResponse(status_code=status.HTTP_200_OK, 
                                content={"message": "Task updated successfully"})
        except Exception as e:
            self.db.close()
            print(e)
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                content={"message": "Internal Server Error"})
        
    def delete_task(self, task_id: str):
        try:
            task = self.db.query(todo_tasks).filter(todo_tasks.id == task_id).first()
            if not task:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, 
                                    content={"message": "Task not found"})
            
            self.db.delete(task)
            self.db.commit()
            self.db.close()

            return JSONResponse(status_code=status.HTTP_200_OK, 
                                content={"message": "Task deleted successfully"})
        except Exception as e:
            self.db.close()
            print(e)
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                content={"message": "Internal Server Error"})
        

@router.get("/tasks")
async def get_tasks(user_id: str, db: Session = Depends(get_db)):
    tasks = Tasks(db)
    return tasks.get_all_tasks(user_id)

@router.post("/add-task")
async def add_task(details: AddTask, db: Session = Depends(get_db)):
    tasks = Tasks(db)
    return tasks.add_task(details)

@router.put("/update-task")
async def update_task(task_id: str, db: Session = Depends(get_db)):
    tasks = Tasks(db)
    return tasks.update_task(task_id)

@router.delete("/delete-task")
async def delete_task(task_id: str, db: Session = Depends(get_db)):
    tasks = Tasks(db)
    return tasks.delete_task(task_id)

