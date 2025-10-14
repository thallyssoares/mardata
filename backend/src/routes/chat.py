
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, List

# Import the shared sessions dictionary from the main application module
from ..main import sessions
from ..services import ai_service

router = APIRouter()

@router.post("/chat/{session_id}")
async def chat_with_data(
    session_id: str,
    question: str = Body(..., embed=True) # Expects a JSON like {"question": "..."}
):
    """
    Handles follow-up questions for a given analysis session.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Analysis session not found.")

    session_data = sessions[session_id]
    original_analysis = session_data["analysis"]
    chat_history = session_data.get("chat_history", [])

    # Get the AI's answer to the follow-up question
    ai_answer = ai_service.get_follow_up_insight(
        original_analysis=original_analysis,
        chat_history=chat_history,
        new_question=question
    )

    # Update the chat history
    session_data["chat_history"].append({"role": "user", "content": question})
    session_data["chat_history"].append({"role": "assistant", "content": ai_answer})

    return {"answer": ai_answer}
