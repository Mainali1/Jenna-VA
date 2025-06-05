"""Health and Fitness Tracking Manager for Jenna Voice Assistant"""

import json
import os
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from backend.utils.helpers import get_logger


class HealthFitnessManager:
    """Manager for health and fitness tracking functionality."""
    
    def __init__(self, data_dir: Path):
        """Initialize the health and fitness manager.
        
        Args:
            data_dir: Directory to store health and fitness data
        """
        self.logger = get_logger("health_fitness_manager")
        self.data_dir = data_dir / "health_fitness"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_file = self.data_dir / "metrics.json"
        self.workouts_file = self.data_dir / "workouts.json"
        self.goals_file = self.data_dir / "goals.json"
        
        # Load existing data or create new files
        self.metrics = self._load_data(self.metrics_file, {})
        self.workouts = self._load_data(self.workouts_file, [])
        self.goals = self._load_data(self.goals_file, [])
        
        self.logger.info("Health and Fitness Manager initialized")
    
    def _load_data(self, file_path: Path, default_data: Any) -> Any:
        """Load data from a JSON file or return default if file doesn't exist.
        
        Args:
            file_path: Path to the JSON file
            default_data: Default data to return if file doesn't exist
            
        Returns:
            Loaded data or default data
        """
        if file_path.exists():
            try:
                with open(file_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading {file_path}: {e}")
                return default_data
        else:
            with open(file_path, "w") as f:
                json.dump(default_data, f)
            return default_data
    
    def _save_data(self, file_path: Path, data: Any) -> bool:
        """Save data to a JSON file.
        
        Args:
            file_path: Path to the JSON file
            data: Data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving {file_path}: {e}")
            return False
    
    # Health Metrics Methods
    
    def add_metric(self, metric_type: str, value: Union[float, int], date: Optional[str] = None) -> bool:
        """Add a health metric measurement.
        
        Args:
            metric_type: Type of metric (weight, steps, heart_rate, etc.)
            value: Metric value
            date: Date of measurement (YYYY-MM-DD), defaults to today
            
        Returns:
            True if successful, False otherwise
        """
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if metric_type not in self.metrics:
            self.metrics[metric_type] = []
        
        self.metrics[metric_type].append({
            "date": date,
            "value": value,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        return self._save_data(self.metrics_file, self.metrics)
    
    def get_metrics(self, metric_type: Optional[str] = None, start_date: Optional[str] = None, 
                   end_date: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get health metrics, optionally filtered by type and date range.
        
        Args:
            metric_type: Type of metric to filter by
            start_date: Start date for filtering (YYYY-MM-DD)
            end_date: End date for filtering (YYYY-MM-DD)
            
        Returns:
            Dictionary of metrics
        """
        if metric_type is not None:
            if metric_type not in self.metrics:
                return {metric_type: []}
            metrics_to_return = {metric_type: self.metrics[metric_type]}
        else:
            metrics_to_return = self.metrics
        
        # Apply date filtering if specified
        if start_date or end_date:
            filtered_metrics = {}
            for m_type, measurements in metrics_to_return.items():
                filtered_measurements = []
                for measurement in measurements:
                    measurement_date = measurement["date"]
                    if ((not start_date or measurement_date >= start_date) and
                        (not end_date or measurement_date <= end_date)):
                        filtered_measurements.append(measurement)
                filtered_metrics[m_type] = filtered_measurements
            return filtered_metrics
        
        return metrics_to_return
    
    # Workout Methods
    
    def add_workout(self, workout_type: str, duration: int, calories: Optional[int] = None,
                   notes: Optional[str] = None, date: Optional[str] = None) -> bool:
        """Add a workout record.
        
        Args:
            workout_type: Type of workout (running, cycling, etc.)
            duration: Duration in minutes
            calories: Estimated calories burned
            notes: Additional notes about the workout
            date: Date of workout (YYYY-MM-DD), defaults to today
            
        Returns:
            True if successful, False otherwise
        """
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        workout = {
            "id": len(self.workouts) + 1,
            "type": workout_type,
            "duration": duration,
            "date": date,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        if calories is not None:
            workout["calories"] = calories
        
        if notes is not None:
            workout["notes"] = notes
        
        self.workouts.append(workout)
        return self._save_data(self.workouts_file, self.workouts)
    
    def get_workouts(self, workout_type: Optional[str] = None, start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get workout records, optionally filtered by type and date range.
        
        Args:
            workout_type: Type of workout to filter by
            start_date: Start date for filtering (YYYY-MM-DD)
            end_date: End date for filtering (YYYY-MM-DD)
            
        Returns:
            List of workout records
        """
        filtered_workouts = self.workouts
        
        if workout_type is not None:
            filtered_workouts = [w for w in filtered_workouts if w["type"] == workout_type]
        
        if start_date is not None:
            filtered_workouts = [w for w in filtered_workouts if w["date"] >= start_date]
        
        if end_date is not None:
            filtered_workouts = [w for w in filtered_workouts if w["date"] <= end_date]
        
        return filtered_workouts
    
    # Fitness Goals Methods
    
    def add_goal(self, goal_type: str, target: Union[float, int], 
                deadline: Optional[str] = None, notes: Optional[str] = None) -> bool:
        """Add a fitness goal.
        
        Args:
            goal_type: Type of goal (weight, steps_per_day, workouts_per_week, etc.)
            target: Target value
            deadline: Goal deadline (YYYY-MM-DD)
            notes: Additional notes about the goal
            
        Returns:
            True if successful, False otherwise
        """
        goal = {
            "id": len(self.goals) + 1,
            "type": goal_type,
            "target": target,
            "created_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "status": "active"
        }
        
        if deadline is not None:
            goal["deadline"] = deadline
        
        if notes is not None:
            goal["notes"] = notes
        
        self.goals.append(goal)
        return self._save_data(self.goals_file, self.goals)
    
    def update_goal_status(self, goal_id: int, status: str) -> bool:
        """Update the status of a goal.
        
        Args:
            goal_id: ID of the goal to update
            status: New status (active, completed, abandoned)
            
        Returns:
            True if successful, False otherwise
        """
        for goal in self.goals:
            if goal["id"] == goal_id:
                goal["status"] = status
                goal["updated_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
                return self._save_data(self.goals_file, self.goals)
        
        self.logger.warning(f"Goal with ID {goal_id} not found")
        return False
    
    def get_goals(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get fitness goals, optionally filtered by status.
        
        Args:
            status: Status to filter by (active, completed, abandoned)
            
        Returns:
            List of goal records
        """
        if status is not None:
            return [g for g in self.goals if g["status"] == status]
        return self.goals
    
    def check_goal_progress(self, goal_id: int) -> Dict[str, Any]:
        """Check progress towards a specific goal.
        
        Args:
            goal_id: ID of the goal to check
            
        Returns:
            Dictionary with goal details and progress information
        """
        for goal in self.goals:
            if goal["id"] == goal_id:
                goal_type = goal["type"]
                target = goal["target"]
                
                # Calculate progress based on goal type
                if goal_type.startswith("weight"):
                    if "weight" in self.metrics and self.metrics["weight"]:
                        latest_weight = self.metrics["weight"][-1]["value"]
                        initial_weight = self.metrics["weight"][0]["value"]
                        progress = abs(latest_weight - initial_weight)
                        remaining = abs(target - latest_weight)
                        return {
                            "goal": goal,
                            "current": latest_weight,
                            "progress": progress,
                            "remaining": remaining,
                            "percent_complete": min(100, int((progress / abs(target - initial_weight)) * 100)) if initial_weight != target else 100
                        }
                
                elif goal_type == "steps_per_day":
                    if "steps" in self.metrics and self.metrics["steps"]:
                        # Calculate average steps over the last 7 days
                        recent_steps = self.metrics["steps"][-7:] if len(self.metrics["steps"]) >= 7 else self.metrics["steps"]
                        avg_steps = sum(entry["value"] for entry in recent_steps) / len(recent_steps)
                        return {
                            "goal": goal,
                            "current": avg_steps,
                            "remaining": max(0, target - avg_steps),
                            "percent_complete": min(100, int((avg_steps / target) * 100))
                        }
                
                elif goal_type == "workouts_per_week":
                    # Count workouts in the last 7 days
                    today = datetime.datetime.now().date()
                    week_ago = (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
                    recent_workouts = self.get_workouts(start_date=week_ago)
                    workout_count = len(recent_workouts)
                    return {
                        "goal": goal,
                        "current": workout_count,
                        "remaining": max(0, target - workout_count),
                        "percent_complete": min(100, int((workout_count / target) * 100))
                    }
                
                # Default response if goal type is not specifically handled
                return {"goal": goal, "progress_calculation": "not_implemented"}
        
        return {"error": f"Goal with ID {goal_id} not found"}