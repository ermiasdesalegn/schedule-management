from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Get Supabase credentials from .env
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Check if credentials exist
if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")

# Create Supabase client
supabase: Client = create_client(supabase_url, supabase_key)



app = FastAPI()


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

@app.get("/")
def read_root():
    return {"Hello": "World"}
@app.get('/dead')
def dead_boy(name:str):
    return {'hello':name}


@app.post('/tasks', status_code=201)
def create_task(task: TaskCreate):
    try:
        response = supabase.table("tasks").insert({
            "title": task.title,
            "description": task.description,
            "completed": task.completed
        }).execute()
        
        return {"message": "Task created successfully", "task": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")
@app.get('/load_task', status_code=200)
def get_tasks():
    try:
        response = supabase.table("tasks").select("*").execute()
        return {"tasks": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading tasks: {str(e)}")
@app.put('/update_task/{task_id}', status_code=200)
def update_task(task_id:int, task:TaskCreate):
    try:
        response = supabase.table("tasks").update({
            "title": task.title,
            "description": task.description,
            "completed": task.completed
        }).eq("id", task_id).execute()
        return {"message": "Task updated successfully", "task": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")

@app.delete('/delete_task/{task_id}', status_code=200)
def delete_task(task_id:int):
    try:
        response = supabase.table("tasks").delete().eq("id", task_id).execute()
        return {"message": "Task deleted successfully", "task": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")

@app.get('/get_task/{task_id}', status_code=200)
def get_task(task_id:int):
    try:
        response = supabase.table("tasks").select("*").eq("id", task_id).execute()
        return {"message": "Task deleted successfully", "task": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading task: {str(e)}")




@app.get('/tasks/filter/{status}', status_code=200)
def filter_tasks(status: str):
    try:
        if status.lower() == "completed":
            response = supabase.table("tasks").select("*").eq("completed", True).execute()
        elif status.lower() == "pending":
            response = supabase.table("tasks").select("*").eq("completed", False).execute()
        else:
            raise HTTPException(status_code=400, detail="Status must be 'completed' or 'pending'")
        
        return {"tasks": response.data, "count": len(response.data)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error filtering tasks: {str(e)}")

@app.get('/tasks/search', status_code=200)
def search_tasks(query: str):
    try:
        response = supabase.table("tasks").select("*").ilike("title", f"%{query}%").execute()
        return {"tasks": response.data, "count": len(response.data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching tasks: {str(e)}")


@app.get('/tasks/stats', status_code=200)
def get_stats():
    try:
        all_tasks = supabase.table("tasks").select("*").execute()
        completed = [t for t in all_tasks.data if t['completed']]
        pending = [t for t in all_tasks.data if not t['completed']]
        
        return {
            "total_tasks": len(all_tasks.data),
            "completed_tasks": len(completed),
            "pending_tasks": len(pending),
            "completion_rate": round(len(completed) / len(all_tasks.data) * 100, 2) if all_tasks.data else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")




@app.delete('/tasks/clear-completed', status_code=200)
def clear_completed():
    try:
        response = supabase.table("tasks").delete().eq("completed", True).execute()
        return {"message": f"Deleted {len(response.data)} completed tasks", "deleted_count": len(response.data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing completed tasks: {str(e)}")