
from fastapi import APIRouter, HTTPException, Body, Depends
from typing import List
from supabase import Client

from ..services import ai_service
from ..lib.dependencies import get_current_user
from ..lib.supabase_client import get_supabase_client
from ..models.user import User


router = APIRouter()

@router.post("/chat/{notebook_id}")
async def chat_with_data(
    notebook_id: str,
    question: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Handles follow-up questions for a given notebook.
    """
    try:
        # 1. Fetch context from Supabase
        notebook_response = supabase.table("notebooks").select(
            "id, user_id, original_file_path, data_schema, analysis_cache, messages(*)"
        ).eq("id", notebook_id).single().execute()

        if not notebook_response.data:
            raise HTTPException(status_code=404, detail="Notebook not found.")

        notebook = notebook_response.data
        
        # Security check: Ensure the user owns the notebook
        if notebook.get('user_id') != str(current_user.id):
            raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this notebook.")

        # 2. Save user's question to the database immediately
        supabase.table("messages").insert({
            "notebook_id": notebook_id,
            "role": "user",
            "content": question
        }).execute()

        # 3. Get AI insight
        ai_response = ai_service.get_follow_up_insight(
            original_analysis=notebook["analysis_cache"],
            chat_history=notebook["messages"],
            new_question=question
        )

        # 4. Save AI's response to the database
        supabase.table("messages").insert({
            "notebook_id": notebook_id,
            "role": "assistant",
            "content": ai_response
        }).execute()

        return {"response": ai_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

