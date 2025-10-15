
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
    question: str = Body(..., embed=True),  # Expects a JSON like {"question": "..."}
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Handles follow-up questions for a given notebook.
    """
    try:
        # Step 1: Fetch the notebook and its history, RLS ensures user ownership.
        # The `select("*, messages(*)")` fetches the notebook and all its messages.
        notebook_response = supabase.table("notebooks").select("id, analysis_cache, messages(*)").eq("id", notebook_id).single().execute()

        if not notebook_response.data:
            raise HTTPException(status_code=404, detail="Notebook not found or you do not have access.")

        notebook_data = notebook_response.data
        original_analysis = notebook_data.get('analysis_cache')
        chat_history = notebook_data.get('messages', [])

        if not original_analysis:
            raise HTTPException(status_code=404, detail="Analysis context not found for this notebook.")

        # Step 2: Get the AI's answer to the follow-up question
        ai_answer = ai_service.get_follow_up_insight(
            original_analysis=original_analysis,
            chat_history=chat_history,
            new_question=question
        )

        # Step 3: Save the new user question and AI answer to the database
        messages_to_insert = [
            {"notebook_id": notebook_id, "role": "user", "content": question},
            {"notebook_id": notebook_id, "role": "assistant", "content": ai_answer}
        ]
        supabase.table("messages").insert(messages_to_insert).execute()

        return {"answer": ai_answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
