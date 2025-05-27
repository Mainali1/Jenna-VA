"""Task Management Feature Implementation"""

import asyncio
import json
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from backend.core.config import Settings
from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException


class TaskPriority(Enum):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(Enum):
    """Status options for tasks."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    ARCHIVED = "archived"


class Task:
    """Represents a task with properties and methods."""
    
    def __init__(
        self,
        task_id: str,
        title: str,
        description: str = "",
        status: Union[TaskStatus, str] = TaskStatus.TODO,
        priority: Union[TaskPriority, str] = TaskPriority.MEDIUM,
        due_date: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        tags: List[str] = None,
        project: Optional[str] = None,
        subtasks: List[Dict[str, Any]] = None,
        notes: str = ""
    ):
        self.task_id = task_id
        self.title = title
        self.description = description
        
        # Convert string to enum if needed
        if isinstance(status, str):
            try:
                self.status = TaskStatus(status)
            except ValueError:
                self.status = TaskStatus.TODO
        else:
            self.status = status
        
        # Convert string to enum if needed
        if isinstance(priority, str):
            try:
                self.priority = TaskPriority(priority)
            except ValueError:
                self.priority = TaskPriority.MEDIUM
        else:
            self.priority = priority
        
        self.due_date = due_date
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or self.created_at
        self.completed_at = completed_at
        self.tags = tags or []
        self.project = project
        self.subtasks = subtasks or []
        self.notes = notes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "tags": self.tags,
            "project": self.project,
            "subtasks": self.subtasks,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create a task from a dictionary."""
        # Convert ISO format strings to datetime objects
        created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        updated_at = datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        due_date = datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None
        completed_at = datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
        
        return cls(
            task_id=data["task_id"],
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", TaskStatus.TODO.value),
            priority=data.get("priority", TaskPriority.MEDIUM.value),
            due_date=due_date,
            created_at=created_at,
            updated_at=updated_at,
            completed_at=completed_at,
            tags=data.get("tags", []),
            project=data.get("project"),
            subtasks=data.get("subtasks", []),
            notes=data.get("notes", "")
        )
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update task properties from a dictionary."""
        if "title" in data:
            self.title = data["title"]
        
        if "description" in data:
            self.description = data["description"]
        
        if "status" in data:
            if isinstance(data["status"], str):
                try:
                    self.status = TaskStatus(data["status"])
                except ValueError:
                    pass  # Keep the current status if invalid
            else:
                self.status = data["status"]
            
            # Update completed_at if status changed to DONE
            if self.status == TaskStatus.DONE and not self.completed_at:
                self.completed_at = datetime.now()
            elif self.status != TaskStatus.DONE:
                self.completed_at = None
        
        if "priority" in data:
            if isinstance(data["priority"], str):
                try:
                    self.priority = TaskPriority(data["priority"])
                except ValueError:
                    pass  # Keep the current priority if invalid
            else:
                self.priority = data["priority"]
        
        if "due_date" in data:
            if isinstance(data["due_date"], str) and data["due_date"]:
                try:
                    self.due_date = datetime.fromisoformat(data["due_date"])
                except ValueError:
                    pass  # Keep the current due date if invalid
            else:
                self.due_date = data["due_date"]
        
        if "tags" in data:
            self.tags = data["tags"]
        
        if "project" in data:
            self.project = data["project"]
        
        if "subtasks" in data:
            self.subtasks = data["subtasks"]
        
        if "notes" in data:
            self.notes = data["notes"]
        
        # Update the updated_at timestamp
        self.updated_at = datetime.now()


class Project:
    """Represents a project that can contain multiple tasks."""
    
    def __init__(
        self,
        project_id: str,
        name: str,
        description: str = "",
        color: str = "#808080",  # Default gray color
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        is_archived: bool = False
    ):
        self.project_id = project_id
        self.name = name
        self.description = description
        self.color = color
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or self.created_at
        self.is_archived = is_archived
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the project to a dictionary."""
        return {
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_archived": self.is_archived
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create a project from a dictionary."""
        # Convert ISO format strings to datetime objects
        created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        updated_at = datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        
        return cls(
            project_id=data["project_id"],
            name=data["name"],
            description=data.get("description", ""),
            color=data.get("color", "#808080"),
            created_at=created_at,
            updated_at=updated_at,
            is_archived=data.get("is_archived", False)
        )
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update project properties from a dictionary."""
        if "name" in data:
            self.name = data["name"]
        
        if "description" in data:
            self.description = data["description"]
        
        if "color" in data:
            self.color = data["color"]
        
        if "is_archived" in data:
            self.is_archived = data["is_archived"]
        
        # Update the updated_at timestamp
        self.updated_at = datetime.now()


class TaskManager:
    """Manages tasks and projects."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir / "tasks"
        self.tasks_file = self.data_dir / "tasks.json"
        self.projects_file = self.data_dir / "projects.json"
        self.logger = get_logger("task_manager")
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize tasks and projects
        self.tasks: Dict[str, Task] = {}
        self.projects: Dict[str, Project] = {}
    
    async def load_data(self) -> None:
        """Load tasks and projects from disk."""
        # Load tasks
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, "r", encoding="utf-8") as f:
                    tasks_data = json.load(f)
                
                for task_data in tasks_data:
                    task = Task.from_dict(task_data)
                    self.tasks[task.task_id] = task
                
                self.logger.info(f"Loaded {len(self.tasks)} tasks from disk")
            except Exception as e:
                self.logger.error(f"Error loading tasks: {e}")
        else:
            self.logger.info("Tasks file does not exist, creating empty file")
            await self.save_tasks()
        
        # Load projects
        if self.projects_file.exists():
            try:
                with open(self.projects_file, "r", encoding="utf-8") as f:
                    projects_data = json.load(f)
                
                for project_data in projects_data:
                    project = Project.from_dict(project_data)
                    self.projects[project.project_id] = project
                
                self.logger.info(f"Loaded {len(self.projects)} projects from disk")
            except Exception as e:
                self.logger.error(f"Error loading projects: {e}")
        else:
            self.logger.info("Projects file does not exist, creating empty file")
            await self.save_projects()
    
    async def save_tasks(self) -> None:
        """Save tasks to disk."""
        try:
            tasks_data = [task.to_dict() for task in self.tasks.values()]
            
            with open(self.tasks_file, "w", encoding="utf-8") as f:
                json.dump(tasks_data, f, indent=2)
            
            self.logger.info(f"Saved {len(self.tasks)} tasks to disk")
        except Exception as e:
            self.logger.error(f"Error saving tasks: {e}")
    
    async def save_projects(self) -> None:
        """Save projects to disk."""
        try:
            projects_data = [project.to_dict() for project in self.projects.values()]
            
            with open(self.projects_file, "w", encoding="utf-8") as f:
                json.dump(projects_data, f, indent=2)
            
            self.logger.info(f"Saved {len(self.projects)} projects to disk")
        except Exception as e:
            self.logger.error(f"Error saving projects: {e}")
    
    # Task methods
    
    async def create_task(self, task_data: Dict[str, Any]) -> Task:
        """Create a new task."""
        # Generate a unique ID if not provided
        if "task_id" not in task_data:
            task_data["task_id"] = f"task-{datetime.now().timestamp()}"
        
        # Create the task
        task = Task.from_dict(task_data)
        
        # Add the task to the dictionary
        self.tasks[task.task_id] = task
        
        # Save tasks to disk
        await self.save_tasks()
        
        return task
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    async def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Optional[Task]:
        """Update an existing task."""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        # Update the task
        task.update(task_data)
        
        # Save tasks to disk
        await self.save_tasks()
        
        return task
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id not in self.tasks:
            return False
        
        # Remove the task
        del self.tasks[task_id]
        
        # Save tasks to disk
        await self.save_tasks()
        
        return True
    
    async def get_all_tasks(self, include_archived: bool = False) -> List[Task]:
        """Get all tasks."""
        if include_archived:
            return list(self.tasks.values())
        else:
            return [task for task in self.tasks.values() if task.status != TaskStatus.ARCHIVED]
    
    async def get_tasks_by_status(self, status: Union[TaskStatus, str]) -> List[Task]:
        """Get tasks by status."""
        # Convert string to enum if needed
        if isinstance(status, str):
            try:
                status_enum = TaskStatus(status)
            except ValueError:
                self.logger.error(f"Invalid status: {status}")
                return []
        else:
            status_enum = status
        
        return [task for task in self.tasks.values() if task.status == status_enum]
    
    async def get_tasks_by_priority(self, priority: Union[TaskPriority, str]) -> List[Task]:
        """Get tasks by priority."""
        # Convert string to enum if needed
        if isinstance(priority, str):
            try:
                priority_enum = TaskPriority(priority)
            except ValueError:
                self.logger.error(f"Invalid priority: {priority}")
                return []
        else:
            priority_enum = priority
        
        return [task for task in self.tasks.values() if task.priority == priority_enum]
    
    async def get_tasks_by_project(self, project_id: str) -> List[Task]:
        """Get tasks by project."""
        return [task for task in self.tasks.values() if task.project == project_id]
    
    async def get_tasks_by_tag(self, tag: str) -> List[Task]:
        """Get tasks by tag."""
        return [task for task in self.tasks.values() if tag in task.tags]
    
    async def get_tasks_due_today(self) -> List[Task]:
        """Get tasks due today."""
        today = datetime.now().date()
        return [
            task for task in self.tasks.values()
            if task.due_date and task.due_date.date() == today and task.status != TaskStatus.DONE
        ]
    
    async def get_tasks_due_this_week(self) -> List[Task]:
        """Get tasks due this week."""
        today = datetime.now().date()
        end_of_week = today + timedelta(days=7 - today.weekday())
        
        return [
            task for task in self.tasks.values()
            if task.due_date and today <= task.due_date.date() <= end_of_week and task.status != TaskStatus.DONE
        ]
    
    async def get_overdue_tasks(self) -> List[Task]:
        """Get overdue tasks."""
        today = datetime.now().date()
        
        return [
            task for task in self.tasks.values()
            if task.due_date and task.due_date.date() < today and task.status != TaskStatus.DONE
        ]
    
    # Project methods
    
    async def create_project(self, project_data: Dict[str, Any]) -> Project:
        """Create a new project."""
        # Generate a unique ID if not provided
        if "project_id" not in project_data:
            project_data["project_id"] = f"project-{datetime.now().timestamp()}"
        
        # Create the project
        project = Project.from_dict(project_data)
        
        # Add the project to the dictionary
        self.projects[project.project_id] = project
        
        # Save projects to disk
        await self.save_projects()
        
        return project
    
    async def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        return self.projects.get(project_id)
    
    async def update_project(self, project_id: str, project_data: Dict[str, Any]) -> Optional[Project]:
        """Update an existing project."""
        project = self.projects.get(project_id)
        if not project:
            return None
        
        # Update the project
        project.update(project_data)
        
        # Save projects to disk
        await self.save_projects()
        
        return project
    
    async def delete_project(self, project_id: str) -> bool:
        """Delete a project and optionally its tasks."""
        if project_id not in self.projects:
            return False
        
        # Remove the project
        del self.projects[project_id]
        
        # Save projects to disk
        await self.save_projects()
        
        return True
    
    async def get_all_projects(self, include_archived: bool = False) -> List[Project]:
        """Get all projects."""
        if include_archived:
            return list(self.projects.values())
        else:
            return [project for project in self.projects.values() if not project.is_archived]
    
    # Statistics and reporting
    
    async def get_task_statistics(self) -> Dict[str, Any]:
        """Get statistics about tasks."""
        total_tasks = len(self.tasks)
        completed_tasks = len([task for task in self.tasks.values() if task.status == TaskStatus.DONE])
        overdue_tasks = len(await self.get_overdue_tasks())
        tasks_by_status = {
            status.value: len([task for task in self.tasks.values() if task.status == status])
            for status in TaskStatus
        }
        tasks_by_priority = {
            priority.value: len([task for task in self.tasks.values() if task.priority == priority])
            for priority in TaskPriority
        }
        tasks_by_project = {}
        for project in self.projects.values():
            count = len([task for task in self.tasks.values() if task.project == project.project_id])
            tasks_by_project[project.name] = count
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": (completed_tasks / total_tasks) if total_tasks > 0 else 0,
            "overdue_tasks": overdue_tasks,
            "tasks_by_status": tasks_by_status,
            "tasks_by_priority": tasks_by_priority,
            "tasks_by_project": tasks_by_project
        }
    
    async def search_tasks(self, query: str) -> List[Task]:
        """Search for tasks by title or description."""
        query = query.lower()
        return [
            task for task in self.tasks.values()
            if query in task.title.lower() or query in task.description.lower()
        ]
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        await self.save_tasks()
        await self.save_projects()
        self.logger.info("Cleaned up TaskManager")