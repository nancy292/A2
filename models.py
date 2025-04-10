from pydantic import BaseModel,Field
from typing import Optional , List, Literal
from datetime import datetime

class Task(BaseModel):
    title: str
    assigned_to: List[str] 
    status: str  
    due_date: str
    completed_date:str

class TaskBoard(BaseModel):
    name: str
    createdBy: str  
    members: List[str]  
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    tasks: List[Task]  

class EditTaskBoardRequest(BaseModel):
    boardId: str
    emails: List[str]

class User(BaseModel):
    name:str
    email:str
