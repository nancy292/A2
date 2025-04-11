from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import TaskBoard , NameRequest ,EmailRequest, TaskNameRequest
from uuid import uuid4 
from google.cloud import firestore
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi import Query, Body

app = FastAPI()
firestore_db = firestore.Client()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Landing page route
@app.get("/", response_class=HTMLResponse)
def get_landingpage(request: Request):
    return templates.TemplateResponse("landingpage.html", {"request": request})



#Checks if user exist if not exist then creates one 
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

#Adding user to a task 
@app.post("/adduserstotask")
async def add_user_to_task(data: EmailRequest):
    print("email is", data.email)
    try:
        does_team_exist = firestore_db.collection('users').where('email','==',data.email).limit(1).get()
        userDetails = {"email":data.email}
        if(len(does_team_exist) == 0):
            firestore_db.collection('users').add(userDetails)
        else:
            # print("User already exist ")
            pass
    except Exception as e:
        print("An error occurred:", e)

    return {"message": "User created"}

#View taskboard page
@app.get("/taskboard", response_class=HTMLResponse)
def get_taskboard_page(request: Request):
    return templates.TemplateResponse("taskboard.html", {"request": request})

#add a taskbaord to database
@app.post("/addtaskboard/create")
async def create_taskboard(taskboard: TaskBoard):
    print("taskboard in create",taskboard)
    taskboard_dict = taskboard.dict()   
    board_id = str(uuid4()) 
    firestore_db.collection("taskboards").document(board_id).set(taskboard_dict)
    return {"message": "TaskBoard created", "id": board_id}

#fetch all the users
@app.get("/getallusers")
async def get_all_users(request:Request):
    users_ref = firestore_db.collection("users")
    users = [doc.to_dict() for doc in users_ref.stream()]
    print("users inside main ",users)
    return {"users": users}

#Check task board name duplicates
@app.post("/checktaskboardname")
async def check_boardName(data: NameRequest):
    try:
        does_board_exist = firestore_db.collection('taskboards').where('name', '==', data.name).limit(1).get()

        if does_board_exist:
            raise HTTPException(status_code=400, detail="Task board already exists")

    except Exception as e:
        print("An error occurred:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"message": "Task board name is available"}

#Check task name duplicates
@app.post("/checktaskname")
async def check_task_name(data: TaskNameRequest):
    try:
        task_board_doc = firestore_db.collection('taskboards').document(data.boardId).get()

        if not task_board_doc.exists:
            raise HTTPException(status_code=404, detail="Task board not found")

        task_board_data = task_board_doc.to_dict()

        for task in task_board_data.get("tasks", []):
            if task.get("title", "").lower() == data.task_title.lower():
                raise HTTPException(status_code=400, detail="Task with the same name already exists in this task board")

    except HTTPException as he:
        raise he
    except Exception as e:
        print("An error occurred:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"message": "Task title is available in this board"}

#Get individual task board
@app.get("/getIndividualTaskBoard/{board_id}")
async def get_individual_taskboard(board_id ,request: Request):
    doc_ref = firestore_db.collection("taskboards").document(board_id)
    doc = doc_ref.get()
    taskboard_data = None
    if doc.exists:
        taskboard_data = doc.to_dict()
    else:
        pass
    
    return {"taskboard_data": taskboard_data}

#Update task baord 
@app.put("/taskboard/{boardId}")
async def edit_taskboard(taskboard: TaskBoard,boardId):
    print("taskbaord ",taskboard,boardId ,type(taskboard))
    updatedTaskBoard = taskboard.dict()
    firestore_db.collection("taskboards").document(boardId).update(updatedTaskBoard)
    return {"board_updated":True}

#get task baord using email
@app.get("/taskboards/{useremail}")
async def get_taskboard_of_user(useremail: str):
    user_tasks = []
    taskboards_ref = firestore_db.collection("taskboards")
    taskboards = taskboards_ref.stream()

    for taskboard in taskboards:
        taskboard_data = taskboard.to_dict()
        board_id = taskboard.id

        if useremail == taskboard_data.get("createdBy") or useremail in taskboard_data.get("members", []):
            taskboard_data["board_id"] = board_id
            user_tasks.append(taskboard_data)

    return {"user_tasks": user_tasks}


#View individual task board
@app.get("/viewIndividualTaskBoard/{board_id}")
async def get_taskboard_using_id(board_id ,request: Request):
    return templates.TemplateResponse("viewIndividualTaskBoard.html", {"request": request, "board_id": board_id})

# Delete task board from Firestore
@app.delete("/taskboard/{boardId}")
async def delete_taskboard(boardId: str):
    firestore_db.collection("taskboards").document(boardId).delete()
    return {"board_deleted": True}

