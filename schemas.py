"""
Database Schemas for BUA-style gear lending app

Each Pydantic model represents a MongoDB collection (collection name is the
lowercased class name).
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class Member(BaseModel):
    """
    Members collection schema
    Collection name: "member"
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    address: Optional[str] = Field(None, description="Address")
    avatar_url: Optional[str] = Field(None, description="Profile photo URL")


class Equipment(BaseModel):
    """
    Equipment items available for lending
    Collection name: "equipment"
    """
    title: str = Field(..., description="Item name")
    category: str = Field(..., description="Category e.g. ski, sykkel, telt")
    condition: str = Field("god", description="Tilstand: ny, god, grei, trenger service")
    description: Optional[str] = Field(None, description="Short description")
    image_url: Optional[str] = Field(None, description="Image URL")
    size: Optional[str] = Field(None, description="Size or specs")
    location: str = Field(..., description="Pickup location e.g. Lierbyen, Tranby")
    tags: List[str] = Field(default_factory=list, description="Search tags")
    is_active: bool = Field(True, description="Visible/available in catalog")


class Reservation(BaseModel):
    """
    Reservations for equipment items
    Collection name: "reservation"
    """
    member_email: str = Field(..., description="Member email")
    equipment_id: str = Field(..., description="ID of equipment document as string")
    start_date: date = Field(..., description="Reservation start date (YYYY-MM-DD)")
    end_date: date = Field(..., description="Reservation end date (YYYY-MM-DD)")
    notes: Optional[str] = Field(None, description="Optional message")


class Report(BaseModel):
    """
    Repair reports or donation offers
    Collection name: "report"
    """
    type: str = Field(..., description="'donation' or 'repair'")
    name: str = Field(..., description="Sender name")
    email: str = Field(..., description="Sender email")
    message: str = Field(..., description="Details")
    equipment_id: Optional[str] = Field(None, description="Related equipment if any")
