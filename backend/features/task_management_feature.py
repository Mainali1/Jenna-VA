"""Task Management Feature Implementation"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.features.task_management import TaskManager, Task, Project, TaskStatus, TaskPriority
from backend.utils.exceptions import FeatureManagerException


class TaskManagementFeature(Feature):
    """Feature for managing tasks and projects."""
    
    def __init__(self, settings: Settings, data_dir: Path):
        super().__init__(settings, data_dir)
        self.logger = get_logger("task_management_feature")
        self.manager: Optional[TaskManager] = None
    
    async def initialize(self) -> None:
        """Initialize the task management feature."""
        try:
            self.logger.info("Initializing TaskManagementFeature")
            
            # Initialize the task manager
            self.manager = TaskManager(self.data_dir)
            await self.manager.load_data()
            
            self.logger.info("TaskManagementFeature initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize TaskManagementFeature: {e}")
            raise FeatureManagerException(f"Failed to initialize TaskManagementFeature: {e}")
    
    async def enable(self) -> None:
        """Enable the task management feature."""
        if not self.manager:
            await self.initialize()
        
        self.logger.info("TaskManagementFeature enabled")
    
    async def disable(self) -> None:
        """Disable the task management feature."""
        self.logger.info("TaskManagementFeature disabled")
    
    async def cleanup(self) -> None:
        """Clean up resources used by the task management feature."""
        if self.manager:
            await self.manager.cleanup()
        self.logger.info("TaskManagementFeature cleaned up")
    
    # Task API methods
    
    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        task = await self.manager.create_task(task_data)
        return task.to_dict()
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        task = await self.manager.get_task(task_id)
        return task.to_dict() if task else None
    
    async def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing task."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        task = await self.manager.update_task(task_id, task_data)
        return task.to_dict() if task else None
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        return await self.manager.delete_task(task_id)
    
    async def get_all_tasks(self, include_archived: bool = False) -> List[Dict[str, Any]]:
        """Get all tasks."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        tasks = await self.manager.get_all_tasks(include_archived)
        return [task.to_dict() for task in tasks]
    
    async def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get tasks by status."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        tasks = await self.manager.get_tasks_by_status(status)
        return [task.to_dict() for task in tasks]
    
    async def get_tasks_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """Get tasks by priority."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        tasks = await self.manager.get_tasks_by_priority(priority)
        return [task.to_dict() for task in tasks]
    
    async def get_tasks_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        """Get tasks by project."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        tasks = await self.manager.get_tasks_by_project(project_id)
        return [task.to_dict() for task in tasks]
    
    async def get_tasks_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get tasks by tag."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        tasks = await self.manager.get_tasks_by_tag(tag)
        return [task.to_dict() for task in tasks]
    
    async def get_tasks_due_today(self) -> List[Dict[str, Any]]:
        """Get tasks due today."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        tasks = await self.manager.get_tasks_due_today()
        return [task.to_dict() for task in tasks]
    
    async def get_tasks_due_this_week(self) -> List[Dict[str, Any]]:
        """Get tasks due this week."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        tasks = await self.manager.get_tasks_due_this_week()
        return [task.to_dict() for task in tasks]
    
    async def get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """Get overdue tasks."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        tasks = await self.manager.get_overdue_tasks()
        return [task.to_dict() for task in tasks]
    
    # Project API methods
    
    async def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        project = await self.manager.create_project(project_data)
        return project.to_dict()
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a project by ID."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        project = await self.manager.get_project(project_id)
        return project.to_dict() if project else None
    
    async def update_project(self, project_id: str, project_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing project."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        project = await self.manager.update_project(project_id, project_data)
        return project.to_dict() if project else None
    
    async def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        return await self.manager.delete_project(project_id)
    
    async def get_all_projects(self, include_archived: bool = False) -> List[Dict[str, Any]]:
        """Get all projects."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        projects = await self.manager.get_all_projects(include_archived)
        return [project.to_dict() for project in projects]
    
    # Statistics and reporting API methods
    
    async def get_task_statistics(self) -> Dict[str, Any]:
        """Get statistics about tasks."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        return await self.manager.get_task_statistics()
    
    async def search_tasks(self, query: str) -> List[Dict[str, Any]]:
        """Search for tasks by title or description."""
        if not self.manager:
            raise FeatureManagerException("TaskManagementFeature not initialized")
        
        tasks = await self.manager.search_tasks(query)
        return [task.to_dict() for task in tasks]