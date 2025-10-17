"""API routes for notebooks."""
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from typing import List, Optional

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

class File(BaseModel):
    id: UUID4
    file_name: str
    file_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    storage_path: str

class Message(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

class NotebookDetails(Notebook):
    messages: List[Message] = []
    files: List[File] = []

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
        response = supabase.table('notebooks').select('*').eq('user_id', str(current_user.id)).order('created_at', desc=True).execute()
        notebooks_data = response.data
        return notebooks_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{notebook_id}", response_model=NotebookDetails)
async def get_notebook_details(
    notebook_id: UUID4,
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Retrieves all details for a specific notebook, including messages and files.
    RLS policies ensure the user can only access their own notebooks.
    """
    try:
        # Fetch the notebook and its related messages and files in one go
        response = supabase.table("notebooks").select("*, messages(*), files(*)").eq("id", str(notebook_id)).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Notebook not found.")

        return response.data
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notebook(
    notebook_id: UUID4,
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Deletes a specific notebook owned by the authenticated user.
    """
    try:
        # Match both notebook_id and user_id for security
        response = supabase.table('notebooks').delete().match({
            'id': str(notebook_id),
            'user_id': str(current_user.id)
        }).execute()

        # The response.data will be empty if no row was found to delete
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found or you do not have permission to delete it.")
        
        return # Return 204 No Content on success

    except Exception as e:
        # Re-raise HTTPException or handle other exceptions
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
