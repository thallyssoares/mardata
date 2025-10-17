
from fastapi import APIRouter, HTTPException, Body, Depends, WebSocket, WebSocketDisconnect
from typing import List
from supabase import Client

from ..services import ai_service
from ..lib.dependencies import get_current_user
from ..lib.supabase_client import get_supabase_client
from ..models.user import User
from ..lib.websocket_manager import manager


router = APIRouter()

@router.websocket("/ws/chat/{notebook_id}")
async def websocket_endpoint(websocket: WebSocket, notebook_id: str):
    await manager.connect(websocket, notebook_id)
    try:
        while True:
            # The backend will send messages, so we just keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(notebook_id)
        print(f"WebSocket disconnected for notebook_id: {notebook_id}")


from arq.connections import ArqRedis
from ..lib.redis_client import get_redis

@router.post("/chat/{notebook_id}")
async def chat_with_data(
    notebook_id: str,
    question: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
    redis: ArqRedis = Depends(get_redis)
):
    """
    Handles follow-up questions for a given notebook by enqueuing a job.
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

        # 2. Prepare the context for the worker
        chat_context = {
            "id": notebook["id"],
            "user_id": notebook["user_id"],
            "original_file_path": notebook["original_file_path"],
            "data_schema": notebook["data_schema"],
            "initial_summary": notebook["analysis_cache"],
            "chat_history": notebook["messages"]
        }

        # 3. Enqueue the job in ARQ (Redis)
        await redis.enqueue_job(
            "process_follow_up_question",
            chat_context,
            question
        )
        
        # 4. Save user's question to the database immediately
        supabase.table("messages").insert({
            "notebook_id": notebook_id,
            "role": "user",
            "content": question
        }).execute()

        return {"status": "processing"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
