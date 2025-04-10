from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import TaskBoard , EditTaskBoardRequest # Import your model 
from uuid import uuid4 
from google.cloud import firestore
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi import Query, Body

app = FastAPI()
firestore_db = firestore.Client()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class EmailRequest(BaseModel):
    email: str

# Root route
@app.get("/", response_class=HTMLResponse)
def get_login(request: Request):
    
    return templates.TemplateResponse("landingpage.html", {"request": request})


@app.post("/CheckAndCreateUser")
async def create_user(data: EmailRequest):
    print("email is", data.email)
    try:
        does_team_exist = firestore_db.collection('users').where('email','==',data.email).limit(1).get()
        userDetails = {"email":data.email}
        if(len(does_team_exist) == 0):
            # print("user does not exist")
            firestore_db.collection('users').add(userDetails)
        else:
            # print("User already exist ")
            pass
    except Exception as e:
        print("An error occurred:", e)

    return {"message": "User created"}

