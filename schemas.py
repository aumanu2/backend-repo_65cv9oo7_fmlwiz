"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Restaurant app schemas

class MenuItem(BaseModel):
    """Menu items available to order. Collection name: "menuitem""" 
    name: str
    description: Optional[str] = None
    price: float
    category: str
    image_url: Optional[str] = None
    is_featured: bool = False

class OrderItem(BaseModel):
    name: str
    quantity: int = Field(1, ge=1)
    price: float = Field(..., ge=0)
    notes: Optional[str] = None

class Order(BaseModel):
    """Customer orders. Collection name: "order"""
    table_id: str = Field(..., description="Table identifier like T-03")
    items: List[OrderItem]
    special_instructions: Optional[str] = None
    status: str = Field("Order Placed", description="Order status: Order Placed, Preparing, Ready, Delivered")
    estimated_time_min: Optional[int] = Field(5, ge=0)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
