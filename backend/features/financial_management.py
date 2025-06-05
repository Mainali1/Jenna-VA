"""Financial Management Manager for Jenna Voice Assistant"""

import json
import os
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from backend.utils.helpers import get_logger


class FinancialManager:
    """Manager for financial management functionality."""
    
    def __init__(self, data_dir: Path):
        """Initialize the financial manager.
        
        Args:
            data_dir: Directory to store financial data
        """
        self.logger = get_logger("financial_manager")
        self.data_dir = data_dir / "financial"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.expenses_file = self.data_dir / "expenses.json"
        self.income_file = self.data_dir / "income.json"
        self.budgets_file = self.data_dir / "budgets.json"
        self.goals_file = self.data_dir / "goals.json"
        
        # Load existing data or create new files
        self.expenses = self._load_data(self.expenses_file, [])
        self.income = self._load_data(self.income_file, [])
        self.budgets = self._load_data(self.budgets_file, {})
        self.goals = self._load_data(self.goals_file, [])
        
        self.logger.info("Financial Manager initialized")
    
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
    
    # Expense Methods
    
    def add_expense(self, amount: float, category: str, description: Optional[str] = None,
                   date: Optional[str] = None) -> bool:
        """Add an expense record.
        
        Args:
            amount: Expense amount
            category: Expense category
            description: Expense description
            date: Date of expense (YYYY-MM-DD), defaults to today
            
        Returns:
            True if successful, False otherwise
        """
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        expense = {
            "id": len(self.expenses) + 1,
            "amount": amount,
            "category": category,
            "date": date,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        if description is not None:
            expense["description"] = description
        
        self.expenses.append(expense)
        return self._save_data(self.expenses_file, self.expenses)
    
    def get_expenses(self, category: Optional[str] = None, start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get expense records, optionally filtered by category and date range.
        
        Args:
            category: Category to filter by
            start_date: Start date for filtering (YYYY-MM-DD)
            end_date: End date for filtering (YYYY-MM-DD)
            
        Returns:
            List of expense records
        """
        filtered_expenses = self.expenses
        
        if category is not None:
            filtered_expenses = [e for e in filtered_expenses if e["category"] == category]
        
        if start_date is not None:
            filtered_expenses = [e for e in filtered_expenses if e["date"] >= start_date]
        
        if end_date is not None:
            filtered_expenses = [e for e in filtered_expenses if e["date"] <= end_date]
        
        return filtered_expenses
    
    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense record.
        
        Args:
            expense_id: ID of the expense to delete
            
        Returns:
            True if successful, False otherwise
        """
        for i, expense in enumerate(self.expenses):
            if expense["id"] == expense_id:
                del self.expenses[i]
                return self._save_data(self.expenses_file, self.expenses)
        
        self.logger.warning(f"Expense with ID {expense_id} not found")
        return False
    
    # Income Methods
    
    def add_income(self, amount: float, source: str, description: Optional[str] = None,
                  date: Optional[str] = None) -> bool:
        """Add an income record.
        
        Args:
            amount: Income amount
            source: Income source
            description: Income description
            date: Date of income (YYYY-MM-DD), defaults to today
            
        Returns:
            True if successful, False otherwise
        """
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        income_entry = {
            "id": len(self.income) + 1,
            "amount": amount,
            "source": source,
            "date": date,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        if description is not None:
            income_entry["description"] = description
        
        self.income.append(income_entry)
        return self._save_data(self.income_file, self.income)
    
    def get_income(self, source: Optional[str] = None, start_date: Optional[str] = None,
                 end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get income records, optionally filtered by source and date range.
        
        Args:
            source: Source to filter by
            start_date: Start date for filtering (YYYY-MM-DD)
            end_date: End date for filtering (YYYY-MM-DD)
            
        Returns:
            List of income records
        """
        filtered_income = self.income
        
        if source is not None:
            filtered_income = [i for i in filtered_income if i["source"] == source]
        
        if start_date is not None:
            filtered_income = [i for i in filtered_income if i["date"] >= start_date]
        
        if end_date is not None:
            filtered_income = [i for i in filtered_income if i["date"] <= end_date]
        
        return filtered_income
    
    def delete_income(self, income_id: int) -> bool:
        """Delete an income record.
        
        Args:
            income_id: ID of the income to delete
            
        Returns:
            True if successful, False otherwise
        """
        for i, income_entry in enumerate(self.income):
            if income_entry["id"] == income_id:
                del self.income[i]
                return self._save_data(self.income_file, self.income)
        
        self.logger.warning(f"Income with ID {income_id} not found")
        return False
    
    # Budget Methods
    
    def set_budget(self, category: str, amount: float, period: str = "monthly") -> bool:
        """Set a budget for a category.
        
        Args:
            category: Expense category
            amount: Budget amount
            period: Budget period (monthly, weekly, yearly)
            
        Returns:
            True if successful, False otherwise
        """
        if period not in ["monthly", "weekly", "yearly"]:
            self.logger.warning(f"Invalid budget period: {period}")
            return False
        
        if period not in self.budgets:
            self.budgets[period] = {}
        
        self.budgets[period][category] = {
            "amount": amount,
            "updated_at": datetime.datetime.now().isoformat()
        }
        
        return self._save_data(self.budgets_file, self.budgets)
    
    def get_budgets(self, period: Optional[str] = None) -> Dict[str, Any]:
        """Get budgets, optionally filtered by period.
        
        Args:
            period: Budget period to filter by (monthly, weekly, yearly)
            
        Returns:
            Dictionary of budgets
        """
        if period is not None:
            if period in self.budgets:
                return {period: self.budgets[period]}
            return {period: {}}
        
        return self.budgets
    
    def delete_budget(self, category: str, period: str = "monthly") -> bool:
        """Delete a budget for a category.
        
        Args:
            category: Expense category
            period: Budget period (monthly, weekly, yearly)
            
        Returns:
            True if successful, False otherwise
        """
        if period in self.budgets and category in self.budgets[period]:
            del self.budgets[period][category]
            return self._save_data(self.budgets_file, self.budgets)
        
        self.logger.warning(f"Budget for {category} in {period} period not found")
        return False
    
    def check_budget_status(self, period: str = "monthly", date: Optional[str] = None) -> Dict[str, Any]:
        """Check budget status for the current period.
        
        Args:
            period: Budget period (monthly, weekly, yearly)
            date: Date to check budget for (YYYY-MM-DD), defaults to today
            
        Returns:
            Dictionary with budget status for each category
        """
        if period not in self.budgets:
            return {"error": f"No budgets set for {period} period"}
        
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
        
        # Determine date range based on period
        if period == "monthly":
            start_date = date_obj.replace(day=1).strftime("%Y-%m-%d")
            # Last day of month calculation
            if date_obj.month == 12:
                end_date = date_obj.replace(year=date_obj.year + 1, month=1, day=1)
            else:
                end_date = date_obj.replace(month=date_obj.month + 1, day=1)
            end_date = (end_date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        elif period == "weekly":
            # Start of week (Monday)
            start_date = (date_obj - datetime.timedelta(days=date_obj.weekday())).strftime("%Y-%m-%d")
            # End of week (Sunday)
            end_date = (date_obj + datetime.timedelta(days=6 - date_obj.weekday())).strftime("%Y-%m-%d")
        elif period == "yearly":
            start_date = date_obj.replace(month=1, day=1).strftime("%Y-%m-%d")
            end_date = date_obj.replace(month=12, day=31).strftime("%Y-%m-%d")
        else:
            return {"error": f"Invalid period: {period}"}
        
        # Get expenses for the period
        period_expenses = self.get_expenses(start_date=start_date, end_date=end_date)
        
        # Calculate spending by category
        spending_by_category = {}
        for expense in period_expenses:
            category = expense["category"]
            amount = expense["amount"]
            
            if category not in spending_by_category:
                spending_by_category[category] = 0
            
            spending_by_category[category] += amount
        
        # Compare with budgets
        budget_status = {}
        for category, budget_info in self.budgets[period].items():
            budget_amount = budget_info["amount"]
            spent = spending_by_category.get(category, 0)
            remaining = budget_amount - spent
            percent_used = (spent / budget_amount) * 100 if budget_amount > 0 else 0
            
            budget_status[category] = {
                "budget": budget_amount,
                "spent": spent,
                "remaining": remaining,
                "percent_used": percent_used,
                "status": "over_budget" if remaining < 0 else "on_track"
            }
        
        # Add categories with spending but no budget
        for category, spent in spending_by_category.items():
            if category not in budget_status:
                budget_status[category] = {
                    "budget": 0,
                    "spent": spent,
                    "remaining": -spent,
                    "percent_used": float('inf'),
                    "status": "no_budget"
                }
        
        return {
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "categories": budget_status,
            "total_budget": sum(b["amount"] for b in self.budgets[period].values()),
            "total_spent": sum(spending_by_category.values()),
            "total_remaining": sum(b["amount"] for b in self.budgets[period].values()) - sum(spending_by_category.values())
        }
    
    # Financial Goals Methods
    
    def add_goal(self, name: str, target_amount: float, current_amount: float = 0,
                deadline: Optional[str] = None, description: Optional[str] = None) -> bool:
        """Add a financial goal.
        
        Args:
            name: Goal name
            target_amount: Target amount
            current_amount: Current amount saved
            deadline: Goal deadline (YYYY-MM-DD)
            description: Goal description
            
        Returns:
            True if successful, False otherwise
        """
        goal = {
            "id": len(self.goals) + 1,
            "name": name,
            "target_amount": target_amount,
            "current_amount": current_amount,
            "created_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "status": "active"
        }
        
        if deadline is not None:
            goal["deadline"] = deadline
        
        if description is not None:
            goal["description"] = description
        
        self.goals.append(goal)
        return self._save_data(self.goals_file, self.goals)
    
    def update_goal_amount(self, goal_id: int, amount: float, is_addition: bool = True) -> bool:
        """Update the current amount of a goal.
        
        Args:
            goal_id: ID of the goal to update
            amount: Amount to add or set
            is_addition: If True, add to current amount; if False, set as new amount
            
        Returns:
            True if successful, False otherwise
        """
        for goal in self.goals:
            if goal["id"] == goal_id:
                if is_addition:
                    goal["current_amount"] += amount
                else:
                    goal["current_amount"] = amount
                
                goal["updated_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
                
                # Check if goal is completed
                if goal["current_amount"] >= goal["target_amount"]:
                    goal["status"] = "completed"
                
                return self._save_data(self.goals_file, self.goals)
        
        self.logger.warning(f"Goal with ID {goal_id} not found")
        return False
    
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
        """Get financial goals, optionally filtered by status.
        
        Args:
            status: Status to filter by (active, completed, abandoned)
            
        Returns:
            List of goal records
        """
        if status is not None:
            return [g for g in self.goals if g["status"] == status]
        return self.goals
    
    def get_goal_progress(self, goal_id: int) -> Dict[str, Any]:
        """Get progress information for a specific goal.
        
        Args:
            goal_id: ID of the goal to check
            
        Returns:
            Dictionary with goal details and progress information
        """
        for goal in self.goals:
            if goal["id"] == goal_id:
                current = goal["current_amount"]
                target = goal["target_amount"]
                percent_complete = (current / target) * 100 if target > 0 else 0
                remaining = target - current
                
                # Calculate time remaining if deadline exists
                time_info = {}
                if "deadline" in goal:
                    deadline = datetime.datetime.strptime(goal["deadline"], "%Y-%m-%d")
                    today = datetime.datetime.now()
                    days_remaining = (deadline - today).days
                    time_info = {
                        "deadline": goal["deadline"],
                        "days_remaining": max(0, days_remaining),
                        "status": "overdue" if days_remaining < 0 else "on_track"
                    }
                
                return {
                    "goal": goal,
                    "current": current,
                    "target": target,
                    "remaining": remaining,
                    "percent_complete": percent_complete,
                    "time_info": time_info
                }
        
        return {"error": f"Goal with ID {goal_id} not found"}
    
    # Summary Methods
    
    def get_financial_summary(self, period: str = "monthly", date: Optional[str] = None) -> Dict[str, Any]:
        """Get a financial summary for the specified period.
        
        Args:
            period: Period for the summary (monthly, weekly, yearly)
            date: Date to generate summary for (YYYY-MM-DD), defaults to today
            
        Returns:
            Dictionary with financial summary information
        """
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
        
        # Determine date range based on period
        if period == "monthly":
            start_date = date_obj.replace(day=1).strftime("%Y-%m-%d")
            # Last day of month calculation
            if date_obj.month == 12:
                end_date = date_obj.replace(year=date_obj.year + 1, month=1, day=1)
            else:
                end_date = date_obj.replace(month=date_obj.month + 1, day=1)
            end_date = (end_date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        elif period == "weekly":
            # Start of week (Monday)
            start_date = (date_obj - datetime.timedelta(days=date_obj.weekday())).strftime("%Y-%m-%d")
            # End of week (Sunday)
            end_date = (date_obj + datetime.timedelta(days=6 - date_obj.weekday())).strftime("%Y-%m-%d")
        elif period == "yearly":
            start_date = date_obj.replace(month=1, day=1).strftime("%Y-%m-%d")
            end_date = date_obj.replace(month=12, day=31).strftime("%Y-%m-%d")
        else:
            return {"error": f"Invalid period: {period}"}
        
        # Get expenses and income for the period
        period_expenses = self.get_expenses(start_date=start_date, end_date=end_date)
        period_income = self.get_income(start_date=start_date, end_date=end_date)
        
        # Calculate totals
        total_expenses = sum(e["amount"] for e in period_expenses)
        total_income = sum(i["amount"] for i in period_income)
        net_cashflow = total_income - total_expenses
        
        # Calculate spending by category
        spending_by_category = {}
        for expense in period_expenses:
            category = expense["category"]
            amount = expense["amount"]
            
            if category not in spending_by_category:
                spending_by_category[category] = 0
            
            spending_by_category[category] += amount
        
        # Calculate income by source
        income_by_source = {}
        for income_entry in period_income:
            source = income_entry["source"]
            amount = income_entry["amount"]
            
            if source not in income_by_source:
                income_by_source[source] = 0
            
            income_by_source[source] += amount
        
        # Get budget status if available
        budget_status = None
        if period in self.budgets and self.budgets[period]:
            budget_status = self.check_budget_status(period, date)
        
        return {
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_cashflow": net_cashflow,
            "savings_rate": (net_cashflow / total_income) * 100 if total_income > 0 else 0,
            "expenses_by_category": spending_by_category,
            "income_by_source": income_by_source,
            "budget_status": budget_status
        }