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
        "message": "Task Management API - Professional Edition",
        "version": "3.0",
        "description": "A comprehensive task management system with advanced features",
        "endpoints": {
            "basic_operations": {
                "get_all": "GET /tasks - Get all tasks with sorting",
                "create": "POST /tasks - Create a new task",
                "get_one": "GET /tasks/{id} - Get a specific task",
                "update": "PUT /tasks/{id} - Update a task (partial updates supported)",
                "delete": "DELETE /tasks/{id} - Delete a task"
            },
            "search_filter": {
                "filter": "GET /tasks/filter/{status} - Filter by completed/pending",
                "search": "GET /tasks/search - Search tasks by title",
                "advanced_search": "GET /tasks/advanced-search - Search with multiple filters",
                "duplicate_check": "POST /tasks/duplicate-check - Check for similar tasks"
            },
            "analytics": {
                "stats": "GET /tasks/stats - Get detailed task statistics",
                "count": "GET /tasks/count - Get task counts by criteria",
                "summary": "GET /tasks/summary - Get comprehensive task summary"
            },
            "sorting_pagination": {
                "recent": "GET /tasks/recent - Get most recent tasks",
                "oldest": "GET /tasks/oldest - Get oldest tasks",
                "longest_titles": "GET /tasks/longest-titles - Get tasks with longest titles",
                "paginated": "GET /tasks/paginated - Get paginated tasks"
            },
            "bulk_operations": {
                "batch_create": "POST /tasks/batch - Create multiple tasks at once",
                "bulk_update": "PATCH /tasks/bulk-update - Update multiple tasks",
                "bulk_delete": "DELETE /tasks/bulk-delete - Delete multiple tasks",
                "mark_all_completed": "PATCH /tasks/bulk/mark-completed - Mark all as completed",
                "mark_all_pending": "PATCH /tasks/bulk/mark-pending - Mark all as pending",
                "clear_completed": "DELETE /tasks/clear-completed - Delete all completed",
                "delete_all": "DELETE /tasks/delete-all - Delete all tasks (requires confirmation)"
            },
            "utilities": {
                "toggle": "PATCH /tasks/{id}/toggle - Quick toggle task completion",
                "export": "GET /tasks/export - Export tasks (JSON/CSV formats)"
            }
        },
        "features": [
            "✅ Full CRUD operations",
            "✅ Advanced search and filtering",
            "✅ Bulk operations (create, update, delete)",
            "✅ Pagination support",
            "✅ Detailed analytics and statistics",
            "✅ Data export (JSON, CSV)",
            "✅ Duplicate detection",
            "✅ Partial updates",
            "✅ Comprehensive error handling"
        ]
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

# ADVANCED FEATURES

@app.get('/tasks/paginated', status_code=200)
def get_tasks_paginated(page: int = 1, page_size: int = 10, sort_by: str = "created_at", order: str = "desc"):
    """Get paginated tasks (useful for large datasets)"""
    try:
        if page < 1:
            raise HTTPException(status_code=400, detail="page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise HTTPException(status_code=400, detail="page_size must be between 1 and 100")
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get total count first
        all_tasks = supabase.table("tasks").select("*", count="exact").execute()
        total_count = len(all_tasks.data)
        
        # Get paginated results
        response = supabase.table("tasks").select("*").order(sort_by, desc=(order == "desc")).range(offset, offset + page_size - 1).execute()
        
        total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
        
        return {
            "tasks": response.data,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting paginated tasks: {str(e)}")

@app.post('/tasks/batch', status_code=201)
def create_tasks_batch(tasks: list[TaskCreate]):
    """Create multiple tasks at once"""
    try:
        if not tasks:
            raise HTTPException(status_code=400, detail="Task list cannot be empty")
        
        if len(tasks) > 50:
            raise HTTPException(status_code=400, detail="Cannot create more than 50 tasks at once")
        
        # Prepare tasks for insertion
        tasks_data = [
            {
                "title": task.title,
                "description": task.description,
                "completed": task.completed
            }
            for task in tasks
        ]
        
        # Insert all tasks
        response = supabase.table("tasks").insert(tasks_data).execute()
        
        return {
            "message": f"Successfully created {len(response.data)} tasks",
            "created_count": len(response.data),
            "tasks": response.data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating batch tasks: {str(e)}")

@app.post('/tasks/duplicate-check', status_code=200)
def check_duplicate_task(title: str):
    """Check if a task with similar title already exists"""
    try:
        # Search for tasks with similar title (case-insensitive)
        response = supabase.table("tasks").select("*").ilike("title", f"%{title}%").execute()
        
        if response.data:
            return {
                "duplicate_found": True,
                "message": f"Found {len(response.data)} similar task(s)",
                "similar_tasks": response.data,
                "count": len(response.data)
            }
        else:
            return {
                "duplicate_found": False,
                "message": "No similar tasks found",
                "similar_tasks": [],
                "count": 0
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking duplicates: {str(e)}")

@app.get('/tasks/count', status_code=200)
def get_task_counts():
    """Get detailed task counts by various criteria"""
    try:
        all_tasks = supabase.table("tasks").select("*").execute()
        
        completed = [t for t in all_tasks.data if t['completed']]
        pending = [t for t in all_tasks.data if not t['completed']]
        
        # Count tasks with descriptions
        with_description = [t for t in all_tasks.data if t.get('description')]
        without_description = [t for t in all_tasks.data if not t.get('description')]
        
        return {
            "total": len(all_tasks.data),
            "by_status": {
                "completed": len(completed),
                "pending": len(pending)
            },
            "by_description": {
                "with_description": len(with_description),
                "without_description": len(without_description)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting task counts: {str(e)}")

@app.delete('/tasks/bulk-delete', status_code=200)
def bulk_delete_tasks(task_ids: list[int]):
    """Delete multiple tasks by their IDs"""
    try:
        if not task_ids:
            raise HTTPException(status_code=400, detail="task_ids list cannot be empty")
        
        if len(task_ids) > 100:
            raise HTTPException(status_code=400, detail="Cannot delete more than 100 tasks at once")
        
        deleted_tasks = []
        not_found = []
        
        for task_id in task_ids:
            # Check if task exists
            existing = supabase.table("tasks").select("*").eq("id", task_id).execute()
            
            if existing.data:
                # Delete task
                supabase.table("tasks").delete().eq("id", task_id).execute()
                deleted_tasks.append(task_id)
            else:
                not_found.append(task_id)
        
        return {
            "message": f"Deleted {len(deleted_tasks)} task(s)",
            "deleted_count": len(deleted_tasks),
            "deleted_ids": deleted_tasks,
            "not_found_ids": not_found,
            "not_found_count": len(not_found)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error bulk deleting tasks: {str(e)}")

@app.get('/tasks/export', status_code=200)
def export_tasks(format: str = "json", status: Optional[str] = None):
    """Export tasks in different formats"""
    try:
        # Get tasks based on status filter
        if status == "completed":
            response = supabase.table("tasks").select("*").eq("completed", True).order("created_at").execute()
        elif status == "pending":
            response = supabase.table("tasks").select("*").eq("completed", False).order("created_at").execute()
        else:
            response = supabase.table("tasks").select("*").order("created_at").execute()
        
        tasks = response.data
        
        if format == "json":
            return {
                "format": "json",
                "exported_at": "now",
                "total_tasks": len(tasks),
                "tasks": tasks
            }
        elif format == "csv":
            # Simple CSV format
            if not tasks:
                csv_content = "id,title,description,completed,created_at\n"
            else:
                csv_content = "id,title,description,completed,created_at\n"
                for task in tasks:
                    csv_content += f"{task['id']},\"{task['title']}\",\"{task.get('description', '')}\",{task['completed']},{task['created_at']}\n"
            
            return {
                "format": "csv",
                "content": csv_content,
                "total_tasks": len(tasks)
            }
        else:
            raise HTTPException(status_code=400, detail="format must be 'json' or 'csv'")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting tasks: {str(e)}")

@app.get('/tasks/summary', status_code=200)
def get_task_summary():
    """Get a comprehensive summary of all tasks"""
    try:
        all_tasks = supabase.table("tasks").select("*").order("created_at", desc=True).execute()
        
        if not all_tasks.data:
            return {
                "message": "No tasks found",
                "total": 0
            }
        
        tasks = all_tasks.data
        completed = [t for t in tasks if t['completed']]
        pending = [t for t in tasks if not t['completed']]
        
        # Calculate average title length
        avg_title_length = sum(len(t['title']) for t in tasks) / len(tasks)
        
        # Find longest and shortest titles
        longest_title = max(tasks, key=lambda t: len(t['title']))
        shortest_title = min(tasks, key=lambda t: len(t['title']))
        
        return {
            "overview": {
                "total_tasks": len(tasks),
                "completed": len(completed),
                "pending": len(pending),
                "completion_rate": round(len(completed) / len(tasks) * 100, 2)
            },
            "title_analysis": {
                "average_length": round(avg_title_length, 2),
                "longest": {
                    "task_id": longest_title['id'],
                    "title": longest_title['title'],
                    "length": len(longest_title['title'])
                },
                "shortest": {
                    "task_id": shortest_title['id'],
                    "title": shortest_title['title'],
                    "length": len(shortest_title['title'])
                }
            },
            "recent_activity": {
                "latest_task": tasks[0],
                "oldest_task": tasks[-1]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting task summary: {str(e)}")

@app.patch('/tasks/bulk-update', status_code=200)
def bulk_update_tasks(task_ids: list[int], update_data: TaskUpdate):
    """Update multiple tasks at once with the same data"""
    try:
        if not task_ids:
            raise HTTPException(status_code=400, detail="task_ids list cannot be empty")
        
        if len(task_ids) > 100:
            raise HTTPException(status_code=400, detail="Cannot update more than 100 tasks at once")
        
        # Build update data
        updates = {}
        if update_data.title is not None:
            updates["title"] = update_data.title
        if update_data.description is not None:
            updates["description"] = update_data.description
        if update_data.completed is not None:
            updates["completed"] = update_data.completed
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        updated_tasks = []
        not_found = []
        
        for task_id in task_ids:
            # Check if task exists
            existing = supabase.table("tasks").select("*").eq("id", task_id).execute()
            
            if existing.data:
                # Update task
                response = supabase.table("tasks").update(updates).eq("id", task_id).execute()
                updated_tasks.extend(response.data)
            else:
                not_found.append(task_id)
        
        return {
            "message": f"Updated {len(updated_tasks)} task(s)",
            "updated_count": len(updated_tasks),
            "updated_tasks": updated_tasks,
            "not_found_ids": not_found,
            "not_found_count": len(not_found)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error bulk updating tasks: {str(e)}")

@app.get('/tasks/oldest', status_code=200)
def get_oldest_tasks(limit: int = 5):
    """Get the oldest tasks"""
    try:
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="limit must be between 1 and 100")
        
        response = supabase.table("tasks").select("*").order("created_at", desc=False).limit(limit).execute()
        
        return {
            "tasks": response.data,
            "count": len(response.data),
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting oldest tasks: {str(e)}")

@app.get('/tasks/longest-titles', status_code=200)
def get_tasks_with_longest_titles(limit: int = 10):
    """Get tasks with the longest titles"""
    try:
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="limit must be between 1 and 100")
        
        all_tasks = supabase.table("tasks").select("*").execute()
        
        if not all_tasks.data:
            return {"tasks": [], "count": 0}
        
        # Sort by title length
        sorted_tasks = sorted(all_tasks.data, key=lambda t: len(t['title']), reverse=True)
        result = sorted_tasks[:limit]
        
        # Add title length to response
        for task in result:
            task['title_length'] = len(task['title'])
        
        return {
            "tasks": result,
            "count": len(result),
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tasks with longest titles: {str(e)}")