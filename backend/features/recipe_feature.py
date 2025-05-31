"""Recipe Feature Implementation using Edamam Recipe Search API"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException
from backend.utils.helpers import is_internet_available


class RecipeFeature(Feature):
    """Feature for searching recipes using Edamam Recipe Search API."""
    
    def __init__(self, settings: Settings):
        super().__init__(
            name="recipe",
            description="Recipe search and information",
            requires_api=True
        )
        self.app_id = None
        self.app_key = None
        self.api_url = "https://api.edamam.com/api/recipes/v2"
        self.logger = get_logger("recipe_feature")
        self.cached_recipes = {}
        self.last_update = None
        self.cache_duration = timedelta(hours=24)  # Cache recipes for 24 hours
    
    def _check_api_requirements(self, settings: Settings) -> bool:
        """Check if Edamam Recipe API credentials are available."""
        return bool(settings.edamam_recipe_app_id and settings.edamam_recipe_app_key)
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Initialize the Recipe feature."""
        try:
            self.logger.info("Initializing RecipeFeature")
            
            # Store API credentials
            self.app_id = settings.edamam_recipe_app_id
            self.app_key = settings.edamam_recipe_app_key
            
            self.logger.info("RecipeFeature initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize RecipeFeature: {e}")
            return False
    
    # API methods
    
    async def search_recipes(self, query: str, diet: Optional[str] = None, 
                            health: Optional[List[str]] = None, 
                            cuisine_type: Optional[str] = None,
                            meal_type: Optional[str] = None,
                            max_results: int = 10) -> Dict[str, Any]:
        """Search for recipes based on query and optional filters.
        
        Args:
            query: Search query (e.g., "chicken soup")
            diet: Diet label (e.g., "balanced", "high-protein", "low-fat")
            health: Health labels (e.g., ["vegan", "gluten-free"])
            cuisine_type: Cuisine type (e.g., "American", "Italian")
            meal_type: Meal type (e.g., "Breakfast", "Lunch", "Dinner")
            max_results: Maximum number of results to return
        """
        if not self.enabled:
            raise FeatureManagerException("RecipeFeature is not enabled")
        
        # Check internet connectivity
        if not is_internet_available():
            self.logger.warning("Internet connection not available for recipe search")
            return {
                "error": "No internet connection available",
                "timestamp": datetime.now().isoformat()
            }
        
        # Check cache first
        cache_key = f"{query}_{diet}_{health}_{cuisine_type}_{meal_type}"
        if cache_key in self.cached_recipes and self.last_update and \
           datetime.now() - self.last_update < self.cache_duration:
            self.logger.info(f"Returning cached recipes for {query}")
            return self.cached_recipes[cache_key]
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "type": "public",
                    "q": query,
                    "app_id": self.app_id,
                    "app_key": self.app_key,
                    "random": "false",
                }
                
                # Add optional filters
                if diet:
                    params["diet"] = diet
                if health:
                    for h in health:
                        params["health"] = h
                if cuisine_type:
                    params["cuisineType"] = cuisine_type
                if meal_type:
                    params["mealType"] = meal_type
                
                async with session.get(self.api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Format the response
                        result = {
                            "query": query,
                            "count": data.get("count", 0),
                            "recipes": []
                        }
                        
                        # Process recipes
                        hits = data.get("hits", [])
                        for i, hit in enumerate(hits):
                            if i >= max_results:
                                break
                                
                            recipe = hit.get("recipe", {})
                            result["recipes"].append({
                                "label": recipe.get("label", ""),
                                "image": recipe.get("image", ""),
                                "source": recipe.get("source", ""),
                                "url": recipe.get("url", ""),
                                "yield": recipe.get("yield", 0),
                                "calories": round(recipe.get("calories", 0)),
                                "total_time": recipe.get("totalTime", 0),
                                "cuisine_type": recipe.get("cuisineType", []),
                                "meal_type": recipe.get("mealType", []),
                                "dish_type": recipe.get("dishType", []),
                                "diet_labels": recipe.get("dietLabels", []),
                                "health_labels": recipe.get("healthLabels", []),
                                "cautions": recipe.get("cautions", []),
                                "ingredients": [{
                                    "text": ingredient.get("text", ""),
                                    "quantity": ingredient.get("quantity", 0),
                                    "measure": ingredient.get("measure", ""),
                                    "food": ingredient.get("food", ""),
                                    "weight": round(ingredient.get("weight", 0)),
                                    "food_category": ingredient.get("foodCategory", "")
                                } for ingredient in recipe.get("ingredients", [])],
                                "nutrients": {
                                    "calories": round(recipe.get("calories", 0)),
                                    "protein": round(recipe.get("totalNutrients", {}).get("PROCNT", {}).get("quantity", 0)),
                                    "fat": round(recipe.get("totalNutrients", {}).get("FAT", {}).get("quantity", 0)),
                                    "carbs": round(recipe.get("totalNutrients", {}).get("CHOCDF", {}).get("quantity", 0)),
                                    "fiber": round(recipe.get("totalNutrients", {}).get("FIBTG", {}).get("quantity", 0)),
                                    "sugar": round(recipe.get("totalNutrients", {}).get("SUGAR", {}).get("quantity", 0))
                                }
                            })
                        
                        # Cache the result
                        self.cached_recipes[cache_key] = result
                        self.last_update = datetime.now()
                        
                        return result
                    else:
                        self.logger.error(f"Error fetching recipes: {response.status}")
                        return {
                            "query": query,
                            "error": f"API error: {response.status}",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            self.logger.error(f"Error searching recipes for {query}: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_recipe_by_id(self, recipe_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific recipe by ID.
        
        Args:
            recipe_id: The Edamam recipe ID
        """
        if not self.enabled:
            raise FeatureManagerException("RecipeFeature is not enabled")
        
        # Check internet connectivity
        if not is_internet_available():
            self.logger.warning("Internet connection not available for recipe details")
            return {
                "error": "No internet connection available",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/{recipe_id}"
                params = {
                    "type": "public",
                    "app_id": self.app_id,
                    "app_key": self.app_key,
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        recipe = data.get("recipe", {})
                        
                        # Format the response
                        result = {
                            "id": recipe_id,
                            "label": recipe.get("label", ""),
                            "image": recipe.get("image", ""),
                            "source": recipe.get("source", ""),
                            "url": recipe.get("url", ""),
                            "yield": recipe.get("yield", 0),
                            "calories": round(recipe.get("calories", 0)),
                            "total_time": recipe.get("totalTime", 0),
                            "cuisine_type": recipe.get("cuisineType", []),
                            "meal_type": recipe.get("mealType", []),
                            "dish_type": recipe.get("dishType", []),
                            "diet_labels": recipe.get("dietLabels", []),
                            "health_labels": recipe.get("healthLabels", []),
                            "cautions": recipe.get("cautions", []),
                            "ingredients": [{
                                "text": ingredient.get("text", ""),
                                "quantity": ingredient.get("quantity", 0),
                                "measure": ingredient.get("measure", ""),
                                "food": ingredient.get("food", ""),
                                "weight": round(ingredient.get("weight", 0)),
                                "food_category": ingredient.get("foodCategory", "")
                            } for ingredient in recipe.get("ingredients", [])],
                            "nutrients": {
                                "calories": round(recipe.get("calories", 0)),
                                "protein": round(recipe.get("totalNutrients", {}).get("PROCNT", {}).get("quantity", 0)),
                                "fat": round(recipe.get("totalNutrients", {}).get("FAT", {}).get("quantity", 0)),
                                "carbs": round(recipe.get("totalNutrients", {}).get("CHOCDF", {}).get("quantity", 0)),
                                "fiber": round(recipe.get("totalNutrients", {}).get("FIBTG", {}).get("quantity", 0)),
                                "sugar": round(recipe.get("totalNutrients", {}).get("SUGAR", {}).get("quantity", 0))
                            },
                            "instructions": recipe.get("instructionLines", [])
                        }
                        
                        return result
                    else:
                        self.logger.error(f"Error fetching recipe details: {response.status}")
                        return {
                            "id": recipe_id,
                            "error": f"API error: {response.status}",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            self.logger.error(f"Error getting recipe details for {recipe_id}: {e}")
            return {
                "id": recipe_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_diet_labels(self) -> Dict[str, Any]:
        """Get available diet labels for filtering recipes."""
        return {
            "diet_labels": [
                "balanced", "high-fiber", "high-protein", "low-carb", 
                "low-fat", "low-sodium"
            ]
        }
    
    def get_health_labels(self) -> Dict[str, Any]:
        """Get available health labels for filtering recipes."""
        return {
            "health_labels": [
                "alcohol-free", "dairy-free", "egg-free", "fish-free", 
                "gluten-free", "keto-friendly", "kosher", "low-sugar", 
                "paleo", "peanut-free", "pescatarian", "pork-free", 
                "red-meat-free", "sesame-free", "shellfish-free", "soy-free", 
                "sugar-conscious", "tree-nut-free", "vegan", "vegetarian", 
                "wheat-free"
            ]
        }
    
    def get_cuisine_types(self) -> Dict[str, Any]:
        """Get available cuisine types for filtering recipes."""
        return {
            "cuisine_types": [
                "American", "Asian", "British", "Caribbean", "Central Europe", 
                "Chinese", "Eastern Europe", "French", "Greek", "Indian", 
                "Italian", "Japanese", "Korean", "Mediterranean", "Mexican", 
                "Middle Eastern", "Nordic", "South American", "South East Asian", 
                "World"
            ]
        }
    
    def get_meal_types(self) -> Dict[str, Any]:
        """Get available meal types for filtering recipes."""
        return {
            "meal_types": [
                "Breakfast", "Brunch", "Lunch", "Dinner", "Snack", "Teatime"
            ]
        }