"""API routes for notebooks."""
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from typing import List

from ..models.user import User
from ..lib.dependencies import get_current_user
from ..lib.supabase_client import get_supabase_client

# Define a Pydantic model for the notebook response to ensure type safety
from pydantic import BaseModel, UUID4
from datetime import datetime

class Notebook(BaseModel):
    id: UUID4
    user_id: UUID4
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Allows Pydantic to read data from ORM models

router = APIRouter()

@router.get("/", response_model=List[Notebook])
async def get_user_notebooks(
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Retrieves all notebooks associated with the currently authenticated user.
    """
    try:
        # The query automatically handles RLS if the client is authenticated with user's token.
        # However, since we use a service key, we explicitly filter by user_id for clarity and security.
        response = supabase.table('notebooks').select('*').eq('user_id', str(current_user.id)).order('created_at', desc=True).execute()
        
        # The data is in response.data
        notebooks_data = response.data
        return notebooks_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
