
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from supabase import Client

from ..services.data_processing import clean_data
from ..services.data_analysis import generate_descriptive_analysis
from ..services.ai_service import get_ai_insights
from ..lib.dependencies import get_current_user
from ..lib.supabase_client import get_supabase_client
from ..models.user import User

router = APIRouter()

@router.post("/upload/")
async def upload_file(
    business_problem: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Receives a file and a business problem, creates a complete notebook
    in the database, and returns the initial analysis.
    """
    try:
        # Step 1: Clean & Analyze data
        cleaned_df = clean_data(file)
        analysis_json = generate_descriptive_analysis(cleaned_df)

        # Step 2: Get initial AI insight
        ai_insight = get_ai_insights(analysis_json, business_problem)

        # Step 3: Create a new notebook in the database
        notebook_data = {
            "user_id": str(current_user.id),
            "title": business_problem[:100],  # Use the problem as a title
            "analysis_cache": analysis_json
        }
        notebook_response = supabase.table("notebooks").insert(notebook_data).execute()
        new_notebook = notebook_response.data[0]
        notebook_id = new_notebook['id']

        # Step 4: (Placeholder) Create a file record in the database
        # In a real scenario, you would upload the file to Supabase Storage first
        # and get the storage_path.
        file_data = {
            "notebook_id": notebook_id,
            "user_id": str(current_user.id),
            "storage_path": f"uploads/{current_user.id}/{notebook_id}/{file.filename}",
            "file_name": file.filename,
            "file_type": file.content_type,
            "file_size_bytes": file.size
        }
        supabase.table("files").insert(file_data).execute()

        # Step 5: Store the initial conversation messages
        messages_to_insert = [
            {"notebook_id": notebook_id, "role": "user", "content": business_problem},
            {"notebook_id": notebook_id, "role": "assistant", "content": ai_insight}
        ]
        supabase.table("messages").insert(messages_to_insert).execute()

        # Step 6: Return the response
        return {
            "notebook_id": notebook_id,
            "filename": file.filename,
            "message": "File processed and notebook created successfully.",
            "ai_insight": ai_insight
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch potential Supabase errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
