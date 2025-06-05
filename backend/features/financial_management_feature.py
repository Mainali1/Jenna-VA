"""Financial Management Feature for Jenna Voice Assistant"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.features.financial_management import FinancialManager
from backend.utils.helpers import get_logger


class FinancialManagementFeature(Feature):
    """Feature for tracking expenses, income, budgets, and financial goals."""
    
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.name = "FinancialManagement"  # Override the default name
        self.description = "Track expenses, income, budgets, and financial goals"
        self.version = "1.0.0"
        self.author = "Jenna Team"
        self.requires_api = False
        self.requires_internet = False
        
        self.manager = None
    
    async def _initialize_impl(self):
        """Initialize the financial management feature."""
        # Create data directory
        data_dir = Path(self.settings.data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize the manager
        self.manager = FinancialManager(data_dir)
        self.logger.info("Financial Management feature initialized")
    
    async def _on_enable(self):
        """Called when the feature is enabled."""
        self.logger.info("Financial Management feature enabled")
    
    async def _on_disable(self):
        """Called when the feature is disabled."""
        self.logger.info("Financial Management feature disabled")
    
    async def cleanup(self):
        """Clean up resources."""
        # Save any pending data
        if self.manager:
            # No specific cleanup needed as data is saved after each operation
            pass
        
        self.logger.info("Financial Management feature cleaned up")
    
    # Expense Methods
    
    async def add_expense(self, amount: float, category: str, 
                         description: Optional[str] = None,
                         date: Optional[str] = None) -> bool:
        """Add an expense record."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot add expense: feature not initialized or enabled")
            return False
        
        return self.manager.add_expense(amount, category, description, date)
    
    async def get_expenses(self, category: Optional[str] = None, 
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get expense records, optionally filtered by category and date range."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot get expenses: feature not initialized or enabled")
            return []
        
        return self.manager.get_expenses(category, start_date, end_date)
    
    async def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense record."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot delete expense: feature not initialized or enabled")
            return False
        
        return self.manager.delete_expense(expense_id)
    
    # Income Methods
    
    async def add_income(self, amount: float, source: str, 
                        description: Optional[str] = None,
                        date: Optional[str] = None) -> bool:
        """Add an income record."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot add income: feature not initialized or enabled")
            return False
        
        return self.manager.add_income(amount, source, description, date)
    
    async def get_income(self, source: Optional[str] = None, 
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get income records, optionally filtered by source and date range."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot get income: feature not initialized or enabled")
            return []
        
        return self.manager.get_income(source, start_date, end_date)
    
    async def delete_income(self, income_id: int) -> bool:
        """Delete an income record."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot delete income: feature not initialized or enabled")
            return False
        
        return self.manager.delete_income(income_id)
    
    # Budget Methods
    
    async def set_budget(self, category: str, amount: float, period: str = "monthly") -> bool:
        """Set a budget for a category."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot set budget: feature not initialized or enabled")
            return False
        
        return self.manager.set_budget(category, amount, period)
    
    async def get_budgets(self, period: Optional[str] = None) -> Dict[str, Any]:
        """Get budgets, optionally filtered by period."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot get budgets: feature not initialized or enabled")
            return {}
        
        return self.manager.get_budgets(period)
    
    async def delete_budget(self, category: str, period: str = "monthly") -> bool:
        """Delete a budget for a category."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot delete budget: feature not initialized or enabled")
            return False
        
        return self.manager.delete_budget(category, period)
    
    async def check_budget_status(self, period: str = "monthly", date: Optional[str] = None) -> Dict[str, Any]:
        """Check budget status for the current period."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot check budget status: feature not initialized or enabled")
            return {"error": "Feature not initialized or enabled"}
        
        return self.manager.check_budget_status(period, date)
    
    # Financial Goals Methods
    
    async def add_goal(self, name: str, target_amount: float, 
                      current_amount: float = 0,
                      deadline: Optional[str] = None, 
                      description: Optional[str] = None) -> bool:
        """Add a financial goal."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot add goal: feature not initialized or enabled")
            return False
        
        return self.manager.add_goal(name, target_amount, current_amount, deadline, description)
    
    async def update_goal_amount(self, goal_id: int, amount: float, is_addition: bool = True) -> bool:
        """Update the current amount of a goal."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot update goal amount: feature not initialized or enabled")
            return False
        
        return self.manager.update_goal_amount(goal_id, amount, is_addition)
    
    async def update_goal_status(self, goal_id: int, status: str) -> bool:
        """Update the status of a goal."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot update goal status: feature not initialized or enabled")
            return False
        
        return self.manager.update_goal_status(goal_id, status)
    
    async def get_goals(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get financial goals, optionally filtered by status."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot get goals: feature not initialized or enabled")
            return []
        
        return self.manager.get_goals(status)
    
    async def get_goal_progress(self, goal_id: int) -> Dict[str, Any]:
        """Get progress information for a specific goal."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot get goal progress: feature not initialized or enabled")
            return {"error": "Feature not initialized or enabled"}
        
        return self.manager.get_goal_progress(goal_id)
    
    # Summary Methods
    
    async def get_financial_summary(self, period: str = "monthly", date: Optional[str] = None) -> Dict[str, Any]:
        """Get a financial summary for the specified period."""
        if not self.initialized or not self.enabled:
            self.logger.warning("Cannot get financial summary: feature not initialized or enabled")
            return {"error": "Feature not initialized or enabled"}
        
        return self.manager.get_financial_summary(period, date)