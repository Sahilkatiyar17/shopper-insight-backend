
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sqlite3
from datetime import datetime
import json

from recommendation_system import RecommendationSystem

# Pydantic models for API
class InteractionBase(BaseModel):
    customer_id: str

class BrowsingInteraction(InteractionBase):
    category: str
    product_id: Optional[int] = None

class PurchaseItem(BaseModel):
    product_id: int
    product_name: str
    product_category: str
    price: float

class PurchaseInteraction(InteractionBase):
    items: List[PurchaseItem]

class RecommendationRequest(BaseModel):
    customer_id: str
    limit: Optional[int] = 10

# Initialize recommendation system
recommendation_system = RecommendationSystem()

# Create FastAPI router that can be imported into main app
from fastapi import APIRouter

recommendation_router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@recommendation_router.get("/{customer_id}")
async def get_recommendations(customer_id: str, limit: int = 10):
    """Get personalized product recommendations for a customer"""
    # First try to get stored recent recommendations
    stored_recs = recommendation_system.get_stored_recommendations(customer_id)
    
    if stored_recs:
        return stored_recs
    
    # If no stored recommendations, generate new ones
    recommendations = recommendation_system.generate_recommendations(customer_id, limit)
    
    if "error" in recommendations:
        raise HTTPException(status_code=404, detail=recommendations["error"])
    
    return recommendations

@recommendation_router.post("/process-browsing")
async def process_browsing(interaction: BrowsingInteraction):
    """Process browsing interaction to update recommendations"""
    result = recommendation_system.process_new_interaction(
        interaction.customer_id, 
        "browsing", 
        {"category": interaction.category, "product_id": interaction.product_id}
    )
    
    return result

@recommendation_router.post("/process-purchase")
async def process_purchase(interaction: PurchaseInteraction):
    """Process purchase interaction to update recommendations"""
    items_dict = [item.dict() for item in interaction.items]
    
    result = recommendation_system.process_new_interaction(
        interaction.customer_id,
        "purchase",
        {"items": items_dict}
    )
    
    return result

# Function to initialize database tables
def initialize_recommendation_database():
    """Initialize the recommendation system database tables"""
    recommendation_system.init_db()
    return {"status": "success", "message": "Recommendation system initialized"}
