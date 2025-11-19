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

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# Example schemas (kept for reference)
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Flowlayers-specific schemas
class Lead(BaseModel):
    """Contact form submissions"""
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    message: Optional[str] = None
    preferred_contact: Optional[str] = Field(None, description="e.g., email, phone, whatsapp")

class AdvisorSubmission(BaseModel):
    """AI Advisor inputs captured for analytics"""
    business_name: str
    industry: str
    employees: Optional[int] = Field(None, ge=1)
    current_tools: Optional[List[str]] = []
    key_processes: Optional[List[str]] = []
    pain_points: Optional[List[str]] = []
    monthly_invoices: Optional[int] = Field(None, ge=0)
    monthly_revenue: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field("USD")
    email: Optional[EmailStr] = None
    created_at: Optional[datetime] = None

# Note: The Flames database viewer can read these from /schema
