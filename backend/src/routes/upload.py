
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..services.data_processing import clean_data
from ..services.data_analysis import generate_descriptive_analysis
from ..services.ai_service import get_ai_insights
from ..main import sessions

router = APIRouter()

@router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    business_problem: str = Form(...)
):
    """
    Receives a file and a business problem, creates an analysis session,
    and returns the initial analysis and a session ID.
    """
    try:
        # Step 1: Clean & Analyze
        cleaned_df = clean_data(file)
        analysis = generate_descriptive_analysis(cleaned_df)

        # Step 2: Get initial AI insight
        insight = get_ai_insights(analysis, business_problem)

        # Step 3: Create a new session
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "analysis": analysis,
            "chat_history": [
                {"role": "user", "content": business_problem},
                {"role": "assistant", "content": insight}
            ]
        }

        # Step 4: Return the response
        return {
            "session_id": session_id,
            "filename": file.filename,
            "message": "File processed and analyzed successfully.",
            "ai_insight": insight
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
