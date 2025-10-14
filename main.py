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
        "message": "Task Management API - Ultimate Edition",
        "version": "4.0",
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
            },
            "fun_features": {
                "random_task": "GET /tasks/random - Get a random task to work on",
                "copy_task": "POST /tasks/{id}/copy - Duplicate tasks (recurring tasks)",
                "search_everywhere": "GET /tasks/search-everywhere - Search in title AND description",
                "needs_attention": "GET /tasks/needs-attention - Find tasks missing descriptions",
                "word_count": "GET /tasks/word-count - Analyze task verbosity",
                "motivational_quote": "GET /tasks/motivational-quote - Get inspired!",
                "completion_streak": "GET /tasks/completion-streak - Track your performance",
                "quick_stats": "GET /tasks/quick-stats - Fast dashboard stats",
                "reverse_all": "PATCH /tasks/reverse-all - Reverse all task statuses",
                "by_title_length": "GET /tasks/by-title-length - Filter by title length"
            },
            "ultimate_features": {
                "today": "GET /tasks/today - Get tasks created today",
                "this_week": "GET /tasks/this-week - Get tasks created this week",
                "compare": "GET /tasks/compare/{id1}/{id2} - Compare two tasks",
                "merge": "POST /tasks/merge - Merge two tasks into one",
                "name_suggestions": "GET /tasks/name-suggestions - Get task name ideas",
                "activity_timeline": "GET /tasks/activity-timeline - View recent activity",
                "empty_check": "GET /tasks/empty-check - Find low-quality tasks",
                "productivity_score": "GET /tasks/productivity-score - Get your score (0-100)",
                "auto_complete_old": "POST /tasks/auto-complete-old - Auto-complete old tasks",
                "alphabet_list": "GET /tasks/alphabet-list - Tasks organized A-Z",
                "health_check": "GET /tasks/health-check - Overall task health report"
            }
        },
        "total_endpoints": 49,
        "features": [
            "✅ Full CRUD operations",
            "✅ Advanced search and filtering",
            "✅ Bulk operations (create, update, delete)",
            "✅ Pagination support",
            "✅ Detailed analytics and statistics",
            "✅ Data export (JSON, CSV)",
            "✅ Duplicate detection",
            "✅ Partial updates",
            "✅ Random task picker",
            "✅ Task copying/duplication",
            "✅ Task merging",
            "✅ Task comparison",
            "✅ Motivational quotes",
            "✅ Completion tracking",
            "✅ Productivity scoring (0-100)",
            "✅ Word count analysis",
            "✅ Health check & quality control",
            "✅ Time-based filtering (today, this week)",
            "✅ Alphabetical organization",
            "✅ Activity timeline",
            "✅ Task name suggestions",
            "✅ Auto-complete old tasks",
            "✅ Comprehensive error handling"
        ],
        "api_info": {
            "documentation": "/docs",
            "alternative_docs": "/redoc",
            "health": "/"
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

# SUPER ADVANCED FEATURES

@app.get('/tasks/random', status_code=200)
def get_random_task(status: Optional[str] = None):
    """Get a random task (useful for picking what to work on next!)"""
    try:
        import random
        
        # Get tasks based on status
        if status == "completed":
            response = supabase.table("tasks").select("*").eq("completed", True).execute()
        elif status == "pending":
            response = supabase.table("tasks").select("*").eq("completed", False).execute()
        else:
            response = supabase.table("tasks").select("*").execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="No tasks found")
        
        # Pick a random task
        random_task = random.choice(response.data)
        
        return {
            "message": "Here's a random task for you!",
            "task": random_task,
            "total_available": len(response.data)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting random task: {str(e)}")

@app.get('/tasks/search-everywhere', status_code=200)
def search_everywhere(query: str):
    """Search in both title AND description"""
    try:
        # Search in title
        title_matches = supabase.table("tasks").select("*").ilike("title", f"%{query}%").execute()
        
        # Search in description
        desc_matches = supabase.table("tasks").select("*").ilike("description", f"%{query}%").execute()
        
        # Combine and remove duplicates
        all_matches = {task['id']: task for task in title_matches.data}
        for task in desc_matches.data:
            all_matches[task['id']] = task
        
        results = list(all_matches.values())
        
        return {
            "query": query,
            "tasks": results,
            "count": len(results),
            "found_in_title": len(title_matches.data),
            "found_in_description": len(desc_matches.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching everywhere: {str(e)}")

@app.get('/tasks/incomplete-with-description', status_code=200)
def get_incomplete_with_description():
    """Get all pending tasks that have descriptions (well-defined tasks)"""
    try:
        all_tasks = supabase.table("tasks").select("*").eq("completed", False).execute()
        
        # Filter tasks that have descriptions
        tasks_with_desc = [t for t in all_tasks.data if t.get('description') and t['description'].strip()]
        
        return {
            "message": "Pending tasks with descriptions",
            "tasks": tasks_with_desc,
            "count": len(tasks_with_desc),
            "total_pending": len(all_tasks.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting incomplete tasks with description: {str(e)}")

@app.get('/tasks/needs-attention', status_code=200)
def get_tasks_needing_attention():
    """Get pending tasks without descriptions (needs more details)"""
    try:
        all_tasks = supabase.table("tasks").select("*").eq("completed", False).execute()
        
        # Filter tasks without descriptions
        tasks_without_desc = [t for t in all_tasks.data if not t.get('description') or not t['description'].strip()]
        
        return {
            "message": "Tasks that need more details",
            "tasks": tasks_without_desc,
            "count": len(tasks_without_desc),
            "suggestion": "Consider adding descriptions to these tasks!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tasks needing attention: {str(e)}")

@app.post('/tasks/{task_id}/copy', status_code=201)
def copy_task(task_id: int, times: int = 1):
    """Duplicate a task (useful for recurring tasks!)"""
    try:
        if times < 1 or times > 10:
            raise HTTPException(status_code=400, detail="times must be between 1 and 10")
        
        # Get original task
        original = supabase.table("tasks").select("*").eq("id", task_id).execute()
        
        if not original.data:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        
        task = original.data[0]
        
        # Create copies
        copies = []
        for i in range(times):
            copy_data = {
                "title": f"{task['title']} (Copy {i+1})" if times > 1 else f"{task['title']} (Copy)",
                "description": task.get('description'),
                "completed": False  # Always start as pending
            }
            copies.append(copy_data)
        
        # Insert all copies
        response = supabase.table("tasks").insert(copies).execute()
        
        return {
            "message": f"Created {times} cop{'ies' if times > 1 else 'y'} of task {task_id}",
            "original_task": task,
            "created_copies": response.data,
            "copies_count": len(response.data)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error copying task: {str(e)}")

@app.get('/tasks/completion-streak', status_code=200)
def get_completion_streak():
    """Get your task completion statistics"""
    try:
        all_tasks = supabase.table("tasks").select("*").order("created_at", desc=True).execute()
        
        if not all_tasks.data:
            return {
                "message": "No tasks found",
                "total_tasks": 0
            }
        
        completed = [t for t in all_tasks.data if t['completed']]
        pending = [t for t in all_tasks.data if not t['completed']]
        
        # Calculate last 10 tasks completion rate
        last_10 = all_tasks.data[:10]
        last_10_completed = [t for t in last_10 if t['completed']]
        
        return {
            "overall": {
                "total_tasks": len(all_tasks.data),
                "completed": len(completed),
                "pending": len(pending),
                "completion_rate": round(len(completed) / len(all_tasks.data) * 100, 2)
            },
            "recent_performance": {
                "last_10_tasks": len(last_10),
                "last_10_completed": len(last_10_completed),
                "last_10_rate": round(len(last_10_completed) / len(last_10) * 100, 2) if last_10 else 0
            },
            "motivation": "Keep going! 🚀" if len(last_10_completed) >= 5 else "You can do this! 💪"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting completion streak: {str(e)}")

@app.get('/tasks/by-title-length', status_code=200)
def get_tasks_by_title_length(min_length: int = 0, max_length: int = 1000):
    """Get tasks filtered by title length"""
    try:
        if min_length < 0:
            raise HTTPException(status_code=400, detail="min_length must be >= 0")
        if max_length > 1000:
            raise HTTPException(status_code=400, detail="max_length must be <= 1000")
        if min_length > max_length:
            raise HTTPException(status_code=400, detail="min_length cannot be greater than max_length")
        
        all_tasks = supabase.table("tasks").select("*").execute()
        
        # Filter by title length
        filtered = [t for t in all_tasks.data if min_length <= len(t['title']) <= max_length]
        
        # Add title_length to each task
        for task in filtered:
            task['title_length'] = len(task['title'])
        
        return {
            "tasks": filtered,
            "count": len(filtered),
            "filters": {
                "min_length": min_length,
                "max_length": max_length
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error filtering by title length: {str(e)}")

@app.get('/tasks/quick-stats', status_code=200)
def get_quick_stats():
    """Get quick dashboard statistics (fast response)"""
    try:
        all_tasks = supabase.table("tasks").select("*").execute()
        
        if not all_tasks.data:
            return {
                "total": 0,
                "completed": 0,
                "pending": 0,
                "completion_percentage": 0
            }
        
        completed_count = sum(1 for t in all_tasks.data if t['completed'])
        total = len(all_tasks.data)
        
        return {
            "total": total,
            "completed": completed_count,
            "pending": total - completed_count,
            "completion_percentage": round(completed_count / total * 100, 1)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting quick stats: {str(e)}")

@app.patch('/tasks/reverse-all', status_code=200)
def reverse_all_task_status():
    """Reverse all task statuses (completed → pending, pending → completed)"""
    try:
        all_tasks = supabase.table("tasks").select("*").execute()
        
        if not all_tasks.data:
            return {"message": "No tasks to reverse", "reversed_count": 0}
        
        reversed_count = 0
        
        for task in all_tasks.data:
            new_status = not task['completed']
            supabase.table("tasks").update({"completed": new_status}).eq("id", task['id']).execute()
            reversed_count += 1
        
        return {
            "message": f"Reversed status of {reversed_count} task(s)",
            "reversed_count": reversed_count,
            "warning": "All completed tasks are now pending, and vice versa!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reversing task statuses: {str(e)}")

@app.get('/tasks/word-count', status_code=200)
def get_task_word_counts():
    """Get tasks sorted by word count in title + description"""
    try:
        all_tasks = supabase.table("tasks").select("*").execute()
        
        if not all_tasks.data:
            return {"tasks": [], "count": 0}
        
        # Calculate word count for each task
        for task in all_tasks.data:
            title_words = len(task['title'].split())
            desc_words = len(task.get('description', '').split()) if task.get('description') else 0
            task['word_count'] = title_words + desc_words
            task['title_words'] = title_words
            task['description_words'] = desc_words
        
        # Sort by word count (descending)
        sorted_tasks = sorted(all_tasks.data, key=lambda t: t['word_count'], reverse=True)
        
        # Calculate average
        avg_words = sum(t['word_count'] for t in sorted_tasks) / len(sorted_tasks)
        
        return {
            "tasks": sorted_tasks,
            "count": len(sorted_tasks),
            "statistics": {
                "average_words_per_task": round(avg_words, 2),
                "most_verbose": sorted_tasks[0]['word_count'] if sorted_tasks else 0,
                "least_verbose": sorted_tasks[-1]['word_count'] if sorted_tasks else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting word counts: {str(e)}")

@app.get('/tasks/motivational-quote', status_code=200)
def get_motivational_quote():
    """Get a motivational quote based on your task completion"""
    try:
        import random
        
        all_tasks = supabase.table("tasks").select("*").execute()
        
        if not all_tasks.data:
            return {
                "quote": "Start your journey with your first task! 🌟",
                "stats": {"total": 0, "completed": 0}
            }
        
        completed_count = sum(1 for t in all_tasks.data if t['completed'])
        total = len(all_tasks.data)
        completion_rate = (completed_count / total * 100) if total > 0 else 0
        
        # Different quotes based on completion rate
        if completion_rate == 0:
            quotes = [
                "Every journey begins with a single step! 🚀",
                "Start small, dream big! ✨",
                "The secret to getting ahead is getting started! 💪"
            ]
        elif completion_rate < 25:
            quotes = [
                "You're just getting started! Keep going! 🌱",
                "Progress, not perfection! 📈",
                "One task at a time! 🎯"
            ]
        elif completion_rate < 50:
            quotes = [
                "You're making great progress! 🌟",
                "Halfway there! Don't stop now! 🔥",
                "Momentum is building! 🚀"
            ]
        elif completion_rate < 75:
            quotes = [
                "You're crushing it! 💪",
                "Amazing progress! Keep it up! ⭐",
                "You're on fire! 🔥"
            ]
        elif completion_rate < 100:
            quotes = [
                "Almost there! Finish strong! 🏆",
                "So close to 100%! You got this! 🎯",
                "The finish line is in sight! 🏁"
            ]
        else:
            quotes = [
                "Perfect score! You're a productivity champion! 🏆",
                "100% complete! Legendary! 👑",
                "All tasks done! You're unstoppable! 🌟"
            ]
        
        return {
            "quote": random.choice(quotes),
            "stats": {
                "total": total,
                "completed": completed_count,
                "pending": total - completed_count,
                "completion_rate": round(completion_rate, 1)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting motivational quote: {str(e)}")

# ULTIMATE FEATURES

@app.get('/tasks/today', status_code=200)
def get_tasks_created_today():
    """Get all tasks created today"""
    try:
        from datetime import datetime, timedelta
        
        # Get today's date range
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)
        
        all_tasks = supabase.table("tasks").select("*").execute()
        
        # Filter tasks created today
        today_tasks = []
        for task in all_tasks.data:
            task_date = datetime.fromisoformat(task['created_at'].replace('Z', '+00:00')).date()
            if task_date == today:
                today_tasks.append(task)
        
        completed = [t for t in today_tasks if t['completed']]
        
        return {
            "message": f"Tasks created today ({today})",
            "tasks": today_tasks,
            "count": len(today_tasks),
            "completed_today": len(completed),
            "pending_today": len(today_tasks) - len(completed)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting today's tasks: {str(e)}")

@app.get('/tasks/this-week', status_code=200)
def get_tasks_this_week():
    """Get all tasks created this week"""
    try:
        from datetime import datetime, timedelta
        
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        
        all_tasks = supabase.table("tasks").select("*").execute()
        
        # Filter tasks created this week
        week_tasks = []
        for task in all_tasks.data:
            task_date = datetime.fromisoformat(task['created_at'].replace('Z', '+00:00')).date()
            if task_date >= week_start:
                week_tasks.append(task)
        
        completed = [t for t in week_tasks if t['completed']]
        
        return {
            "message": f"Tasks created this week (since {week_start})",
            "tasks": week_tasks,
            "count": len(week_tasks),
            "completed_this_week": len(completed),
            "pending_this_week": len(week_tasks) - len(completed),
            "week_start": str(week_start)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting this week's tasks: {str(e)}")

@app.get('/tasks/compare/{task_id_1}/{task_id_2}', status_code=200)
def compare_tasks(task_id_1: int, task_id_2: int):
    """Compare two tasks side by side"""
    try:
        # Get both tasks
        task1_response = supabase.table("tasks").select("*").eq("id", task_id_1).execute()
        task2_response = supabase.table("tasks").select("*").eq("id", task_id_2).execute()
        
        if not task1_response.data:
            raise HTTPException(status_code=404, detail=f"Task {task_id_1} not found")
        if not task2_response.data:
            raise HTTPException(status_code=404, detail=f"Task {task_id_2} not found")
        
        task1 = task1_response.data[0]
        task2 = task2_response.data[0]
        
        # Compare properties
        comparison = {
            "task_1": task1,
            "task_2": task2,
            "comparison": {
                "same_status": task1['completed'] == task2['completed'],
                "title_length_diff": abs(len(task1['title']) - len(task2['title'])),
                "both_have_description": bool(task1.get('description')) and bool(task2.get('description')),
                "word_count_diff": abs(
                    len(task1['title'].split()) + len(task1.get('description', '').split()) -
                    len(task2['title'].split()) - len(task2.get('description', '').split())
                )
            }
        }
        
        return comparison
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing tasks: {str(e)}")

@app.post('/tasks/merge', status_code=201)
def merge_tasks(task_id_1: int, task_id_2: int, delete_originals: bool = False):
    """Merge two tasks into one new task"""
    try:
        # Get both tasks
        task1_response = supabase.table("tasks").select("*").eq("id", task_id_1).execute()
        task2_response = supabase.table("tasks").select("*").eq("id", task_id_2).execute()
        
        if not task1_response.data:
            raise HTTPException(status_code=404, detail=f"Task {task_id_1} not found")
        if not task2_response.data:
            raise HTTPException(status_code=404, detail=f"Task {task_id_2} not found")
        
        task1 = task1_response.data[0]
        task2 = task2_response.data[0]
        
        # Create merged task
        merged_title = f"{task1['title']} + {task2['title']}"
        merged_desc = ""
        if task1.get('description') and task2.get('description'):
            merged_desc = f"{task1['description']} | {task2['description']}"
        elif task1.get('description'):
            merged_desc = task1['description']
        elif task2.get('description'):
            merged_desc = task2['description']
        
        merged_completed = task1['completed'] and task2['completed']
        
        # Create the merged task
        new_task = {
            "title": merged_title,
            "description": merged_desc if merged_desc else None,
            "completed": merged_completed
        }
        
        created = supabase.table("tasks").insert(new_task).execute()
        
        # Optionally delete originals
        if delete_originals:
            supabase.table("tasks").delete().eq("id", task_id_1).execute()
            supabase.table("tasks").delete().eq("id", task_id_2).execute()
        
        return {
            "message": "Tasks merged successfully",
            "merged_task": created.data[0],
            "original_tasks_deleted": delete_originals,
            "source_task_ids": [task_id_1, task_id_2]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error merging tasks: {str(e)}")

@app.get('/tasks/name-suggestions', status_code=200)
def get_task_name_suggestions(category: str = "general"):
    """Get random task name suggestions for inspiration"""
    try:
        import random
        
        suggestions = {
            "general": [
                "Review project documentation",
                "Update task list",
                "Organize workspace",
                "Send follow-up emails",
                "Plan next week's schedule"
            ],
            "work": [
                "Prepare presentation slides",
                "Review team progress",
                "Schedule client meeting",
                "Update project roadmap",
                "Code review for PR #123"
            ],
            "personal": [
                "Call family member",
                "Workout session",
                "Read for 30 minutes",
                "Meal prep for week",
                "Organize closet"
            ],
            "shopping": [
                "Buy groceries",
                "Get birthday gift",
                "Order office supplies",
                "Purchase new running shoes",
                "Restock pantry items"
            ],
            "health": [
                "Schedule doctor appointment",
                "Take daily vitamins",
                "Go for a walk",
                "Drink 8 glasses of water",
                "Meditate for 10 minutes"
            ]
        }
        
        if category not in suggestions:
            available = list(suggestions.keys())
            raise HTTPException(status_code=400, detail=f"category must be one of: {available}")
        
        return {
            "category": category,
            "suggestions": random.sample(suggestions[category], min(3, len(suggestions[category]))),
            "all_categories": list(suggestions.keys())
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting name suggestions: {str(e)}")

@app.get('/tasks/activity-timeline', status_code=200)
def get_activity_timeline(limit: int = 20):
    """Get a timeline of recent task activities"""
    try:
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="limit must be between 1 and 100")
        
        all_tasks = supabase.table("tasks").select("*").order("created_at", desc=True).limit(limit).execute()
        
        timeline = []
        for task in all_tasks.data:
            timeline.append({
                "timestamp": task['created_at'],
                "action": "created",
                "task_id": task['id'],
                "task_title": task['title'],
                "status": "completed" if task['completed'] else "pending"
            })
        
        return {
            "timeline": timeline,
            "count": len(timeline),
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting activity timeline: {str(e)}")

@app.get('/tasks/empty-check', status_code=200)
def check_empty_tasks():
    """Find tasks with very short or empty titles/descriptions"""
    try:
        all_tasks = supabase.table("tasks").select("*").execute()
        
        short_title = [t for t in all_tasks.data if len(t['title'].strip()) < 5]
        no_description = [t for t in all_tasks.data if not t.get('description') or not t['description'].strip()]
        very_short = [t for t in all_tasks.data if len(t['title'].strip()) < 3]
        
        return {
            "quality_issues": {
                "very_short_titles": {
                    "count": len(very_short),
                    "tasks": very_short
                },
                "short_titles": {
                    "count": len(short_title),
                    "tasks": short_title
                },
                "missing_descriptions": {
                    "count": len(no_description),
                    "tasks": no_description
                }
            },
            "total_tasks": len(all_tasks.data),
            "recommendation": "Consider adding more details to these tasks for better clarity"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking empty tasks: {str(e)}")

@app.get('/tasks/productivity-score', status_code=200)
def calculate_productivity_score():
    """Calculate your productivity score (0-100)"""
    try:
        all_tasks = supabase.table("tasks").select("*").execute()
        
        if not all_tasks.data:
            return {
                "score": 0,
                "grade": "N/A",
                "message": "Create some tasks to see your productivity score!"
            }
        
        total = len(all_tasks.data)
        completed = sum(1 for t in all_tasks.data if t['completed'])
        with_description = sum(1 for t in all_tasks.data if t.get('description') and t['description'].strip())
        
        # Calculate score components
        completion_score = (completed / total) * 40  # 40 points for completion
        description_score = (with_description / total) * 30  # 30 points for having descriptions
        volume_score = min(len(all_tasks.data) / 50 * 30, 30)  # 30 points for having tasks (max at 50 tasks)
        
        total_score = completion_score + description_score + volume_score
        
        # Determine grade
        if total_score >= 90:
            grade = "A+"
        elif total_score >= 80:
            grade = "A"
        elif total_score >= 70:
            grade = "B"
        elif total_score >= 60:
            grade = "C"
        elif total_score >= 50:
            grade = "D"
        else:
            grade = "F"
        
        return {
            "score": round(total_score, 1),
            "grade": grade,
            "breakdown": {
                "completion": round(completion_score, 1),
                "description_quality": round(description_score, 1),
                "task_volume": round(volume_score, 1)
            },
            "stats": {
                "total_tasks": total,
                "completed_tasks": completed,
                "tasks_with_descriptions": with_description
            },
            "message": _get_score_message(total_score)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating productivity score: {str(e)}")

def _get_score_message(score):
    """Helper function to get message based on score"""
    if score >= 90:
        return "Outstanding! You're a productivity superstar! 🌟"
    elif score >= 80:
        return "Excellent work! Keep it up! 🎉"
    elif score >= 70:
        return "Great job! You're doing well! 👍"
    elif score >= 60:
        return "Good effort! Room for improvement! 📈"
    elif score >= 50:
        return "Not bad! Keep working at it! 💪"
    else:
        return "Let's boost that score! You can do it! 🚀"

@app.post('/tasks/auto-complete-old', status_code=200)
def auto_complete_old_tasks(days_old: int = 30):
    """Automatically mark old pending tasks as completed"""
    try:
        from datetime import datetime, timedelta
        
        if days_old < 1 or days_old > 365:
            raise HTTPException(status_code=400, detail="days_old must be between 1 and 365")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        all_tasks = supabase.table("tasks").select("*").eq("completed", False).execute()
        
        old_tasks = []
        for task in all_tasks.data:
            task_date = datetime.fromisoformat(task['created_at'].replace('Z', '+00:00'))
            if task_date < cutoff_date:
                old_tasks.append(task)
        
        # Mark old tasks as completed
        updated_count = 0
        for task in old_tasks:
            supabase.table("tasks").update({"completed": True}).eq("id", task['id']).execute()
            updated_count += 1
        
        return {
            "message": f"Auto-completed {updated_count} old task(s)",
            "updated_count": updated_count,
            "cutoff_date": str(cutoff_date),
            "days_old": days_old,
            "updated_tasks": old_tasks
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error auto-completing old tasks: {str(e)}")

@app.get('/tasks/alphabet-list', status_code=200)
def get_tasks_alphabetically():
    """Get tasks organized alphabetically by first letter"""
    try:
        all_tasks = supabase.table("tasks").select("*").execute()
        
        if not all_tasks.data:
            return {"alphabet": {}, "total": 0}
        
        # Group by first letter
        alphabet_dict = {}
        for task in all_tasks.data:
            first_letter = task['title'][0].upper() if task['title'] else '#'
            if not first_letter.isalpha():
                first_letter = '#'
            
            if first_letter not in alphabet_dict:
                alphabet_dict[first_letter] = []
            alphabet_dict[first_letter].append(task)
        
        # Sort each group
        for letter in alphabet_dict:
            alphabet_dict[letter].sort(key=lambda t: t['title'].lower())
        
        # Convert to sorted list
        sorted_alphabet = dict(sorted(alphabet_dict.items()))
        
        return {
            "alphabet": sorted_alphabet,
            "letters_used": list(sorted_alphabet.keys()),
            "total_tasks": len(all_tasks.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error organizing alphabetically: {str(e)}")

@app.get('/tasks/health-check', status_code=200)
def task_health_check():
    """Check the overall health of your task list"""
    try:
        all_tasks = supabase.table("tasks").select("*").execute()
        
        if not all_tasks.data:
            return {
                "health_status": "No tasks",
                "score": 0,
                "message": "Create some tasks to get started!"
            }
        
        total = len(all_tasks.data)
        completed = sum(1 for t in all_tasks.data if t['completed'])
        with_desc = sum(1 for t in all_tasks.data if t.get('description') and t['description'].strip())
        short_titles = sum(1 for t in all_tasks.data if len(t['title'].strip()) < 5)
        long_titles = sum(1 for t in all_tasks.data if len(t['title']) > 100)
        
        # Calculate health issues
        issues = []
        warnings = []
        
        if completed / total < 0.2:
            issues.append("Low completion rate (<20%)")
        if with_desc / total < 0.5:
            warnings.append("Many tasks lack descriptions")
        if short_titles > 0:
            warnings.append(f"{short_titles} task(s) have very short titles")
        if long_titles > 0:
            warnings.append(f"{long_titles} task(s) have very long titles")
        
        # Overall health score
        health_score = 100
        health_score -= len(issues) * 20
        health_score -= len(warnings) * 10
        health_score = max(0, health_score)
        
        if health_score >= 90:
            status = "Excellent"
        elif health_score >= 70:
            status = "Good"
        elif health_score >= 50:
            status = "Fair"
        else:
            status = "Needs Attention"
        
        return {
            "health_status": status,
            "health_score": health_score,
            "issues": issues,
            "warnings": warnings,
            "statistics": {
                "total_tasks": total,
                "completion_rate": round(completed / total * 100, 1),
                "tasks_with_descriptions": with_desc,
                "short_titles": short_titles,
                "long_titles": long_titles
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking task health: {str(e)}")