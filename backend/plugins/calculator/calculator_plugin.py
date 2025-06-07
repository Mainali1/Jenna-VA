"""Calculator Plugin for Jenna VA.

A simple calculator plugin that provides basic arithmetic operations.
"""

import math
import operator
from typing import Dict, Any, List, Union, Optional

from ...core.feature_manager import Feature


class CalculatorFeature(Feature):
    """Implementation of the calculator feature."""
    
    def __init__(self):
        super().__init__()
        self.name = "calculator"
        self.description = "A simple calculator plugin for Jenna VA"
        self.version = "0.1.0"
        self.author = "Jenna VA Team"
        self.requires_api = False
        self.requires_internet = False
        
        # Default settings
        self.precision = 2
        self.scientific_notation = False
        
        # Define operations
        self.operations = {
            'add': operator.add,
            'subtract': operator.sub,
            'multiply': operator.mul,
            'divide': operator.truediv,
            'power': operator.pow,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log10,
            'ln': math.log,
            'abs': abs,
            'round': round,
            'floor': math.floor,
            'ceil': math.ceil,
        }
    
    async def _initialize_impl(self, settings):
        """Initialize the feature implementation."""
        # Load settings if available
        if hasattr(settings, 'plugins') and 'calculator' in settings.plugins:
            calculator_settings = settings.plugins['calculator']
            if 'default_precision' in calculator_settings:
                self.precision = calculator_settings['default_precision']
            if 'scientific_notation' in calculator_settings:
                self.scientific_notation = calculator_settings['scientific_notation']
        
        self.logger.info(f"Initialized calculator plugin with precision={self.precision}, "
                       f"scientific_notation={self.scientific_notation}")
        return True
    
    async def _check_api_requirements(self):
        """Check if API requirements are met."""
        # No API requirements for this plugin
        return True
    
    async def _on_enable(self):
        """Called when the feature is enabled."""
        self.logger.info("Calculator plugin enabled")
    
    async def _on_disable(self):
        """Called when the feature is disabled."""
        self.logger.info("Calculator plugin disabled")
    
    async def calculate(self, operation: str, a: Union[int, float], b: Optional[Union[int, float]] = None) -> Dict[str, Any]:
        """Perform a calculation.
        
        Args:
            operation: The operation to perform (add, subtract, multiply, divide, etc.)
            a: First operand
            b: Second operand (optional for unary operations like sqrt, sin, etc.)
            
        Returns:
            Dict containing the result and operation details
        """
        if not self.enabled:
            raise Exception("Calculator feature is not enabled")
        
        operation = operation.lower()
        
        if operation not in self.operations:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "available_operations": list(self.operations.keys())
            }
        
        try:
            # Unary operations
            if operation in ['sqrt', 'sin', 'cos', 'tan', 'log', 'ln', 'abs', 'floor', 'ceil']:
                if b is not None:
                    self.logger.warning(f"Ignoring second operand for unary operation {operation}")
                
                result = self.operations[operation](a)
            
            # Binary operations
            else:
                if b is None:
                    return {
                        "success": False,
                        "error": f"Operation {operation} requires two operands"
                    }
                
                # Special case for division by zero
                if operation == 'divide' and b == 0:
                    return {
                        "success": False,
                        "error": "Division by zero"
                    }
                
                result = self.operations[operation](a, b)
            
            # Format the result
            if self.scientific_notation and abs(result) > 1e6:
                formatted_result = f"{result:.{self.precision}e}"
            else:
                formatted_result = round(result, self.precision)
                # Convert to int if it's a whole number
                if formatted_result == int(formatted_result):
                    formatted_result = int(formatted_result)
            
            return {
                "success": True,
                "operation": operation,
                "operands": [a, b] if b is not None else [a],
                "result": result,
                "formatted_result": formatted_result
            }
            
        except Exception as e:
            self.logger.error(f"Calculation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_operations(self) -> List[str]:
        """Get a list of available operations.
        
        Returns:
            List of operation names
        """
        return list(self.operations.keys())
    
    async def set_precision(self, precision: int) -> Dict[str, Any]:
        """Set the decimal precision for calculations.
        
        Args:
            precision: Number of decimal places
            
        Returns:
            Dict with the updated setting
        """
        if not self.enabled:
            raise Exception("Calculator feature is not enabled")
        
        if precision < 0 or precision > 15:
            return {
                "success": False,
                "error": "Precision must be between 0 and 15"
            }
        
        self.precision = precision
        return {
            "success": True,
            "precision": precision
        }
    
    async def set_scientific_notation(self, enabled: bool) -> Dict[str, Any]:
        """Enable or disable scientific notation for large numbers.
        
        Args:
            enabled: Whether to enable scientific notation
            
        Returns:
            Dict with the updated setting
        """
        if not self.enabled:
            raise Exception("Calculator feature is not enabled")
        
        self.scientific_notation = enabled
        return {
            "success": True,
            "scientific_notation": enabled
        }