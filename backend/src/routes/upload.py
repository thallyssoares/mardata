
import uuid
import tempfile
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from supabase import Client

from ..services.chunk_processing import process_spreadsheet_in_chunks
from ..services.ai_service import get_ai_insights
from ..services.optimization_service import convert_to_parquet_and_update_record
from ..lib.dependencies import get_current_user
from ..lib.supabase_client import get_supabase_client
from ..models.user import User

router = APIRouter()

async def run_ai_analysis_and_save(
    notebook_id: str,
    business_problem: str,
    analysis_json: str,
    supabase: Client,
    temp_path: str,
    original_file_name: str,
    user_id: str
):
    """Background task to run AI analysis, save results, and optimize for future use."""
    # Step 1: Get initial AI insight
    ai_insight = await get_ai_insights(analysis_json, business_problem, notebook_id)

    # Step 2: Store the initial conversation messages
    messages_to_insert = [
        {"notebook_id": notebook_id, "role": "user", "content": business_problem},
        {"notebook_id": notebook_id, "role": "assistant", "content": ai_insight}
    ]
    supabase.table("messages").insert(messages_to_insert).execute()

    # Step 3: After analysis, convert the original file to Parquet for optimization
    await convert_to_parquet_and_update_record(
        original_file_path=temp_path,
        original_file_name=original_file_name,
        notebook_id=notebook_id,
        user_id=user_id,
        supabase=supabase
    )


@router.post("/upload/")
async def upload_file(
    background_tasks: BackgroundTasks,
    business_problem: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Receives a file and a business problem, creates a notebook, 
    and starts the analysis and optimization in the background.
    """
    # Create a temporary file to store the upload
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)

    try:
        with open(temp_path, "wb") as f:
            f.write(file.file.read())

        # Step 1: Analyze data using the chunk-based processor
        analysis_json = process_spreadsheet_in_chunks(temp_path, file.filename)

        # Step 2: Create a new notebook in the database
        notebook_data = {
            "user_id": str(current_user.id),
            "title": business_problem[:100],  # Use the problem as a title
            "analysis_cache": analysis_json
        }
        notebook_response = supabase.table("notebooks").insert(notebook_data).execute()
        new_notebook = notebook_response.data[0]
        notebook_id = new_notebook['id']

        # Step 3: Create a file record
        file_data = {
            "notebook_id": notebook_id,
            "user_id": str(current_user.id),
            "storage_path": f"uploads/{current_user.id}/{notebook_id}/{file.filename}",
            "file_name": file.filename,
            "file_type": file.content_type,
            "file_size_bytes": file.size
        }
        supabase.table("files").insert(file_data).execute()

        # Step 4: Add the AI analysis and Parquet conversion to background tasks
        background_tasks.add_task(
            run_ai_analysis_and_save,
            notebook_id=notebook_id, 
            business_problem=business_problem, 
            analysis_json=analysis_json, 
            supabase=supabase,
            temp_path=temp_path,
            original_file_name=file.filename,
            user_id=str(current_user.id)
        )

        # Step 5: Return the immediate response
        return {
            "notebook_id": notebook_id,
            "filename": file.filename,
            "message": "File uploaded. Analysis has started and will be streamed.",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # If something fails before the background task, clean up the temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            os.rmdir(temp_dir)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
