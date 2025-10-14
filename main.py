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

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

@app.get("/")
def read_root():
    return {
        "message": "Task Management API",
        "version": "2.0",
        "endpoints": {
            "tasks": "GET /tasks - Get all tasks with sorting",
            "create": "POST /tasks - Create a new task",
            "get_one": "GET /tasks/{id} - Get a specific task",
            "update": "PUT /tasks/{id} - Update a task",
            "delete": "DELETE /tasks/{id} - Delete a task",
            "toggle": "PATCH /tasks/{id}/toggle - Toggle task completion",
            "filter": "GET /tasks/filter/{status} - Filter by completed/pending",
            "search": "GET /tasks/search - Search tasks by title",
            "advanced_search": "GET /tasks/advanced-search - Search with filters",
            "recent": "GET /tasks/recent - Get recent tasks",
            "stats": "GET /tasks/stats - Get task statistics",
            "clear_completed": "DELETE /tasks/clear-completed - Delete all completed tasks",
            "bulk_complete": "PATCH /tasks/bulk/mark-completed - Mark all as completed",
            "bulk_pending": "PATCH /tasks/bulk/mark-pending - Mark all as pending"
        }
    }


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
@app.get('/tasks', status_code=200)
def get_all_tasks(sort_by: str = "created_at", order: str = "desc"):
    try:
        # Validate sort options
        valid_sorts = ["created_at", "title", "completed"]
        if sort_by not in valid_sorts:
            raise HTTPException(status_code=400, detail=f"sort_by must be one of: {valid_sorts}")
        
        # Validate order
        if order not in ["asc", "desc"]:
            raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")
        
        # Get tasks with sorting
        response = supabase.table("tasks").select("*").order(sort_by, desc=(order == "desc")).execute()
        
        return {
            "tasks": response.data,
            "count": len(response.data),
            "sorted_by": sort_by,
            "order": order
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading tasks: {str(e)}")
@app.put('/tasks/{task_id}', status_code=200)
def update_task(task_id: int, task: TaskUpdate):
    try:
        # Check if task exists
        existing = supabase.table("tasks").select("*").eq("id", task_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        
        # Build update data (only non-None fields)
        update_data = {}
        if task.title is not None:
            update_data["title"] = task.title
        if task.description is not None:
            update_data["description"] = task.description
        if task.completed is not None:
            update_data["completed"] = task.completed
        
        # Check if there's anything to update
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Update task
        response = supabase.table("tasks").update(update_data).eq("id", task_id).execute()
        
        return {"message": "Task updated successfully", "task": response.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")

@app.delete('/tasks/{task_id}', status_code=200)
def delete_task(task_id: int):
    try:
        # Check if task exists first
        existing = supabase.table("tasks").select("*").eq("id", task_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        
        # Delete the task
        supabase.table("tasks").delete().eq("id", task_id).execute()
        
        return {
            "message": "Task deleted successfully",
            "deleted_task_id": task_id,
            "deleted_task": existing.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")

@app.get('/tasks/{task_id}', status_code=200)
def get_task(task_id: int):
    try:
        response = supabase.table("tasks").select("*").eq("id", task_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        
        return {"task": response.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting task: {str(e)}")




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
def get_detailed_stats():
    """Get detailed task statistics"""
    try:
        all_tasks = supabase.table("tasks").select("*").order("created_at", desc=True).execute()
        
        if not all_tasks.data:
            return {
                "total_tasks": 0,
                "completed_tasks": 0,
                "pending_tasks": 0,
                "completion_rate": 0,
                "message": "No tasks found"
            }
        
        completed = [t for t in all_tasks.data if t['completed']]
        pending = [t for t in all_tasks.data if not t['completed']]
        
        # Calculate additional stats
        total = len(all_tasks.data)
        completion_rate = round(len(completed) / total * 100, 2) if total > 0 else 0
        
        return {
            "total_tasks": total,
            "completed_tasks": len(completed),
            "pending_tasks": len(pending),
            "completion_rate": completion_rate,
            "status_breakdown": {
                "completed_percentage": completion_rate,
                "pending_percentage": round(100 - completion_rate, 2)
            },
            "latest_task": all_tasks.data[0] if all_tasks.data else None,
            "oldest_task": all_tasks.data[-1] if all_tasks.data else None
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

# NEW FEATURES

@app.patch('/tasks/{task_id}/toggle', status_code=200)
def toggle_task_completion(task_id: int):
    """Quick toggle task completion status"""
    try:
        # Get current task
        current = supabase.table("tasks").select("completed").eq("id", task_id).execute()
        
        if not current.data:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        
        # Toggle the completed status
        new_status = not current.data[0]['completed']
        
        # Update task
        response = supabase.table("tasks").update({"completed": new_status}).eq("id", task_id).execute()
        
        return {
            "message": f"Task marked as {'completed' if new_status else 'pending'}",
            "task": response.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling task: {str(e)}")

@app.get('/tasks/recent', status_code=200)
def get_recent_tasks(limit: int = 5):
    """Get the most recently created tasks"""
    try:
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="limit must be between 1 and 100")
        
        response = supabase.table("tasks").select("*").order("created_at", desc=True).limit(limit).execute()
        
        return {
            "tasks": response.data,
            "count": len(response.data),
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recent tasks: {str(e)}")

@app.get('/tasks/advanced-search', status_code=200)
def advanced_search(
    query: Optional[str] = None,
    completed: Optional[bool] = None,
    sort_by: str = "created_at",
    order: str = "desc"
):
    """Search tasks with multiple filters and sorting"""
    try:
        # Start with base query
        db_query = supabase.table("tasks").select("*")
        
        # Add filters if provided
        if query:
            db_query = db_query.ilike("title", f"%{query}%")
        
        if completed is not None:
            db_query = db_query.eq("completed", completed)
        
        # Add sorting
        db_query = db_query.order(sort_by, desc=(order == "desc"))
        
        # Execute
        response = db_query.execute()
        
        return {
            "tasks": response.data,
            "count": len(response.data),
            "filters": {
                "query": query,
                "completed": completed,
                "sort_by": sort_by,
                "order": order
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in advanced search: {str(e)}")

@app.patch('/tasks/bulk/mark-completed', status_code=200)
def mark_all_completed():
    """Mark all pending tasks as completed"""
    try:
        response = supabase.table("tasks").update({"completed": True}).eq("completed", False).execute()
        return {
            "message": "All pending tasks marked as completed",
            "updated_count": len(response.data),
            "tasks": response.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking tasks as completed: {str(e)}")

@app.patch('/tasks/bulk/mark-pending', status_code=200)
def mark_all_pending():
    """Mark all completed tasks as pending"""
    try:
        response = supabase.table("tasks").update({"completed": False}).eq("completed", True).execute()
        return {
            "message": "All completed tasks marked as pending",
            "updated_count": len(response.data),
            "tasks": response.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking tasks as pending: {str(e)}")

@app.delete('/tasks/delete-all', status_code=200)
def delete_all_tasks(confirm: bool = False):
    """Delete all tasks (requires confirmation)"""
    try:
        if not confirm:
            raise HTTPException(
                status_code=400,
                detail="Please confirm deletion by adding ?confirm=true to the URL"
            )
        
        # Get all tasks first
        all_tasks = supabase.table("tasks").select("*").execute()
        count = len(all_tasks.data)
        
        if count == 0:
            return {"message": "No tasks to delete", "deleted_count": 0}
        
        # Delete all
        supabase.table("tasks").delete().neq("id", 0).execute()  # Delete where id != 0 (basically all)
        
        return {
            "message": f"All tasks deleted successfully",
            "deleted_count": count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting all tasks: {str(e)}")