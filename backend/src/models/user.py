"""User models."""
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

class User(BaseModel):
    id: uuid.UUID
    email: Optional[EmailStr] = None
    # Add other fields from Supabase's auth.users table as needed
