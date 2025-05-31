"""Nutrition Feature Implementation using Edamam Nutrition Analysis API"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException
from backend.utils.helpers import is_internet_available


class NutritionFeature(Feature):
    """Feature for analyzing nutrition information using Edamam Nutrition Analysis API."""
    
    def __init__(self, settings: Settings):
        super().__init__(
            name="nutrition",
            description="Nutrition analysis for ingredients and recipes",
            requires_api=True
        )
        self.app_id = None
        self.app_key = None
        self.nutrition_api_url = "https://api.edamam.com/api/nutrition-details"
        self.food_api_url = "https://api.edamam.com/api/food-database/v2/parser"
        self.logger = get_logger("nutrition_feature")
        self.cached_analyses = {}
        self.cached_foods = {}
        self.last_update = None
        self.cache_duration = timedelta(days=7)  # Cache nutrition data for 7 days
    
    def _check_api_requirements(self, settings: Settings) -> bool:
        """Check if Edamam Nutrition API credentials are available."""
        return bool(settings.edamam_nutrition_app_id and settings.edamam_nutrition_app_key)
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Initialize the Nutrition feature."""
        try:
            self.logger.info("Initializing NutritionFeature")
            
            # Store API credentials
            self.app_id = settings.edamam_nutrition_app_id
            self.app_key = settings.edamam_nutrition_app_key
            
            self.logger.info("NutritionFeature initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize NutritionFeature: {e}")
            return False
    
    # API methods
    
    async def analyze_recipe(self, title: str, ingredients: List[str]) -> Dict[str, Any]:
        """Analyze nutrition information for a recipe with multiple ingredients.
        
        Args:
            title: Recipe title
            ingredients: List of ingredient lines (e.g., ["1 cup rice", "2 tbsp olive oil"])
        """
        if not self.enabled:
            raise FeatureManagerException("NutritionFeature is not enabled")
        
        # Check internet connectivity
        if not is_internet_available():
            self.logger.warning("Internet connection not available for nutrition analysis")
            return {
                "error": "No internet connection available",
                "timestamp": datetime.now().isoformat()
            }
        
        # Check cache first
        cache_key = f"{title}_{','.join(ingredients)}"
        if cache_key in self.cached_analyses and self.last_update and \
           datetime.now() - self.last_update < self.cache_duration:
            self.logger.info(f"Returning cached nutrition analysis for {title}")
            return self.cached_analyses[cache_key]
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "title": title,
                    "ingr": ingredients
                }
                
                url = f"{self.nutrition_api_url}?app_id={self.app_id}&app_key={self.app_key}"
                
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Format the response
                        result = {
                            "title": title,
                            "ingredients": ingredients,
                            "calories": data.get("calories", 0),
                            "total_weight": round(data.get("totalWeight", 0)),
                            "diet_labels": data.get("dietLabels", []),
                            "health_labels": data.get("healthLabels", []),
                            "cautions": data.get("cautions", []),
                            "nutrients": {}
                        }
                        
                        # Process nutrients
                        nutrients = data.get("totalNutrients", {})
                        for nutrient_id, nutrient_data in nutrients.items():
                            result["nutrients"][nutrient_id] = {
                                "label": nutrient_data.get("label", ""),
                                "quantity": round(nutrient_data.get("quantity", 0), 2),
                                "unit": nutrient_data.get("unit", "")
                            }
                        
                        # Add daily percentages
                        daily = data.get("totalDaily", {})
                        result["daily_percentages"] = {}
                        for nutrient_id, nutrient_data in daily.items():
                            result["daily_percentages"][nutrient_id] = {
                                "label": nutrient_data.get("label", ""),
                                "quantity": round(nutrient_data.get("quantity", 0), 2),
                                "unit": nutrient_data.get("unit", "")
                            }
                        
                        # Cache the result
                        self.cached_analyses[cache_key] = result
                        self.last_update = datetime.now()
                        
                        return result
                    else:
                        error_data = await response.text()
                        self.logger.error(f"Error analyzing recipe: {response.status}, {error_data}")
                        return {
                            "title": title,
                            "error": f"API error: {response.status}",
                            "message": error_data,
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            self.logger.error(f"Error analyzing recipe {title}: {e}")
            return {
                "title": title,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def analyze_ingredient(self, ingredient: str) -> Dict[str, Any]:
        """Analyze nutrition information for a single ingredient.
        
        Args:
            ingredient: Ingredient text (e.g., "1 cup rice")
        """
        # For single ingredients, we'll use the same method but wrap in a list
        return await self.analyze_recipe("Single Ingredient", [ingredient])
    
    async def search_food(self, query: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Search for food items in the Edamam Food Database.
        
        Args:
            query: Food search query (e.g., "apple")
            category: Optional food category filter
        """
        if not self.enabled:
            raise FeatureManagerException("NutritionFeature is not enabled")
        
        # Check internet connectivity
        if not is_internet_available():
            self.logger.warning("Internet connection not available for food search")
            return {
                "error": "No internet connection available",
                "timestamp": datetime.now().isoformat()
            }
        
        # Check cache first
        cache_key = f"{query}_{category}"
        if cache_key in self.cached_foods and self.last_update and \
           datetime.now() - self.last_update < self.cache_duration:
            self.logger.info(f"Returning cached food search for {query}")
            return self.cached_foods[cache_key]
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "app_id": self.app_id,
                    "app_key": self.app_key,
                    "ingr": query
                }
                
                # Add category filter if provided
                if category:
                    params["category"] = category
                
                async with session.get(self.food_api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Format the response
                        result = {
                            "query": query,
                            "foods": []
                        }
                        
                        # Process food items
                        hints = data.get("hints", [])
                        for hint in hints:
                            food = hint.get("food", {})
                            measures = hint.get("measures", [])
                            
                            food_item = {
                                "food_id": food.get("foodId", ""),
                                "label": food.get("label", ""),
                                "category": food.get("category", ""),
                                "category_label": food.get("categoryLabel", ""),
                                "image": food.get("image", ""),
                                "nutrients": {
                                    "energy": round(food.get("nutrients", {}).get("ENERC_KCAL", 0)),
                                    "protein": round(food.get("nutrients", {}).get("PROCNT", 0), 1),
                                    "fat": round(food.get("nutrients", {}).get("FAT", 0), 1),
                                    "carbs": round(food.get("nutrients", {}).get("CHOCDF", 0), 1),
                                    "fiber": round(food.get("nutrients", {}).get("FIBTG", 0), 1)
                                },
                                "measures": [{
                                    "uri": measure.get("uri", ""),
                                    "label": measure.get("label", ""),
                                    "weight": round(measure.get("weight", 0))
                                } for measure in measures]
                            }
                            
                            result["foods"].append(food_item)
                        
                        # Cache the result
                        self.cached_foods[cache_key] = result
                        self.last_update = datetime.now()
                        
                        return result
                    else:
                        self.logger.error(f"Error searching food: {response.status}")
                        return {
                            "query": query,
                            "error": f"API error: {response.status}",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            self.logger.error(f"Error searching food {query}: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_food_categories(self) -> Dict[str, Any]:
        """Get available food categories for filtering."""
        return {
            "food_categories": [
                "generic-foods", "generic-meals", "packaged-foods", "fast-foods",
                "restaurant-foods", "food-supplements"
            ]
        }
    
    def get_nutrient_info(self) -> Dict[str, Any]:
        """Get information about nutrients and their recommended daily values."""
        return {
            "nutrients": {
                "ENERC_KCAL": {"label": "Energy", "unit": "kcal", "daily_value": 2000},
                "FAT": {"label": "Total Fat", "unit": "g", "daily_value": 65},
                "FASAT": {"label": "Saturated Fat", "unit": "g", "daily_value": 20},
                "FATRN": {"label": "Trans Fat", "unit": "g", "daily_value": 0},
                "FAMS": {"label": "Monounsaturated Fat", "unit": "g", "daily_value": None},
                "FAPU": {"label": "Polyunsaturated Fat", "unit": "g", "daily_value": None},
                "CHOCDF": {"label": "Total Carbohydrate", "unit": "g", "daily_value": 300},
                "FIBTG": {"label": "Dietary Fiber", "unit": "g", "daily_value": 25},
                "SUGAR": {"label": "Sugars", "unit": "g", "daily_value": 50},
                "PROCNT": {"label": "Protein", "unit": "g", "daily_value": 50},
                "CHOLE": {"label": "Cholesterol", "unit": "mg", "daily_value": 300},
                "NA": {"label": "Sodium", "unit": "mg", "daily_value": 2400},
                "CA": {"label": "Calcium", "unit": "mg", "daily_value": 1300},
                "MG": {"label": "Magnesium", "unit": "mg", "daily_value": 420},
                "K": {"label": "Potassium", "unit": "mg", "daily_value": 4700},
                "FE": {"label": "Iron", "unit": "mg", "daily_value": 18},
                "ZN": {"label": "Zinc", "unit": "mg", "daily_value": 11},
                "P": {"label": "Phosphorus", "unit": "mg", "daily_value": 1250},
                "VITA_RAE": {"label": "Vitamin A", "unit": "µg", "daily_value": 900},
                "VITC": {"label": "Vitamin C", "unit": "mg", "daily_value": 90},
                "THIA": {"label": "Thiamin (B1)", "unit": "mg", "daily_value": 1.2},
                "RIBF": {"label": "Riboflavin (B2)", "unit": "mg", "daily_value": 1.3},
                "NIA": {"label": "Niacin (B3)", "unit": "mg", "daily_value": 16},
                "VITB6A": {"label": "Vitamin B6", "unit": "mg", "daily_value": 1.7},
                "FOLDFE": {"label": "Folate (Equivalent)", "unit": "µg", "daily_value": 400},
                "VITB12": {"label": "Vitamin B12", "unit": "µg", "daily_value": 2.4},
                "VITD": {"label": "Vitamin D", "unit": "µg", "daily_value": 20},
                "TOCPHA": {"label": "Vitamin E", "unit": "mg", "daily_value": 15},
                "VITK1": {"label": "Vitamin K", "unit": "µg", "daily_value": 120}
            }
        }