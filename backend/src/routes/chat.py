
from fastapi import APIRouter, HTTPException, Body, Depends
from typing import List, Dict, Any
from supabase import Client
from pydantic import BaseModel
import logging

from ..services import ai_service
from ..lib.dependencies import get_current_user
from ..lib.supabase_client import get_supabase_client
from ..models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequestBody(BaseModel):
    question: str
    chat_history: List[Dict[str, Any]]
    statistical_summary: Dict[str, Any]

@router.post("/chat/{notebook_id}")
async def chat_with_data(
    notebook_id: str,
    payload: ChatRequestBody,
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Handles follow-up questions for a given notebook.
    """
    try:
        # 1. Fetch notebook to validate ownership and get file path
        notebook_response = supabase.table("notebooks").select("user_id, files(storage_path)").eq("id", notebook_id).single().execute()
        if not notebook_response.data or notebook_response.data.get('user_id') != str(current_user.id):
            raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this notebook.")
        
        notebook = notebook_response.data
        
        # 2. Save user's question
        user_message_response = supabase.table("messages").insert({
            "notebook_id": notebook_id,
            "role": "user",
            "content": payload.question
        }).execute()
        logger.info(f"User message saved: {user_message_response.data}")

        # 3. Get the file path
        if not notebook.get('files'):
            raise HTTPException(status_code=404, detail="No file associated with this notebook.")
        file_path = notebook['files'][0]['storage_path']
        logger.info(f"Retrieved file_path from DB: {file_path}")

        # 4. Get AI insight
        ai_response = ai_service.get_follow_up_insight(
            original_analysis=payload.statistical_summary,
            chat_history=payload.chat_history,
            new_question=payload.question,
            file_path=file_path,
            supabase_client=supabase
        )

        # 5. Save AI's response to the database
        ai_message_response = supabase.table("messages").insert({
            "notebook_id": notebook_id,
            "role": "assistant",
            "content": ai_response
        }).execute()
        logger.info(f"AI message saved: {ai_message_response.data}")

        return {"response": ai_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")