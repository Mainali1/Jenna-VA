"""Health and Fitness Tracking Feature for Jenna Voice Assistant"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.features.health_fitness import HealthFitnessManager
from backend.utils.helpers import get_logger


class HealthFitnessFeature(Feature):
    """Feature for tracking health and fitness metrics, workouts, and goals."""
    
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.name = "HealthFitness"  # Override the default name
        self.description = "Track health metrics, workouts, and fitness goals"
        self.version = "1.0.0"
        self.author = "Jenna Team"
        self.requires_api = False
        self.requires_internet = False
        
        self.manager = None
    
    async def _initialize_impl(self):
        """Initialize the health and fitness feature."""
        # Create data directory
        data_dir = Path(self.settings.data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize the manager
        self.manager = HealthFitnessManager(data_dir)
        self.logger.info("Health and Fitness feature initialized")
    
    async def _on_enable(self):
        """Called when the feature is enabled."""
        self.logger.info("Health and Fitness feature enabled")
    
    async def _on_disable(self):
        """Called when the feature is disabled."""
        self.logger.info("Health and Fitness feature disabled")
    
    async def cleanup(self):
        """Clean up resources."""
        # Save any pending data
        if self.manager:
            # No specific cleanup needed as data is saved after each operation
            pass
        
        self.logger.info("Health and Fitness feature cleaned up")
    
    # Health Metrics Methods
    
    async def add_metric(self, metric_type: str, value: Union[float, int], date: Optional[str] = None) -> bool:
        """Add a health metric measurement."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot add metric: feature not initialized or enabled")
            return False
        
        return self.manager.add_metric(metric_type, value, date)
    
    async def get_metrics(self, metric_type: Optional[str] = None, 
                         start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get health metrics, optionally filtered by type and date range."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot get metrics: feature not initialized or enabled")
            return {}
        
        return self.manager.get_metrics(metric_type, start_date, end_date)
    
    # Workout Methods
    
    async def add_workout(self, workout_type: str, duration: int, 
                         calories: Optional[int] = None,
                         notes: Optional[str] = None, 
                         date: Optional[str] = None) -> bool:
        """Add a workout record."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot add workout: feature not initialized or enabled")
            return False
        
        return self.manager.add_workout(workout_type, duration, calories, notes, date)
    
    async def get_workouts(self, workout_type: Optional[str] = None, 
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get workout records, optionally filtered by type and date range."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot get workouts: feature not initialized or enabled")
            return []
        
        return self.manager.get_workouts(workout_type, start_date, end_date)
    
    # Fitness Goals Methods
    
    async def add_goal(self, goal_type: str, target: Union[float, int], 
                      deadline: Optional[str] = None, 
                      notes: Optional[str] = None) -> bool:
        """Add a fitness goal."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot add goal: feature not initialized or enabled")
            return False
        
        return self.manager.add_goal(goal_type, target, deadline, notes)
    
    async def update_goal_status(self, goal_id: int, status: str) -> bool:
        """Update the status of a goal."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot update goal: feature not initialized or enabled")
            return False
        
        return self.manager.update_goal_status(goal_id, status)
    
    async def get_goals(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get fitness goals, optionally filtered by status."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot get goals: feature not initialized or enabled")
            return []
        
        return self.manager.get_goals(status)
    
    async def check_goal_progress(self, goal_id: int) -> Dict[str, Any]:
        """Check progress towards a specific goal."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot check goal progress: feature not initialized or enabled")
            return {"error": "Feature not initialized or enabled"}
        
        return self.manager.check_goal_progress(goal_id)