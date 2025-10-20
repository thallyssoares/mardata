import uuid
import tempfile
import os
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from supabase import Client

from ..services.chunk_processing import process_spreadsheet_in_chunks
from ..services.ai_service import get_ai_insights
from ..services.optimization_service import convert_to_parquet_and_update_record
from ..lib.dependencies import get_current_user
from ..lib.supabase_client import get_supabase_client
from ..models.user import User

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
async def upload_file_and_process(
    background_tasks: BackgroundTasks,
    business_problem: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Handles file upload, creates a notebook, triggers analysis, and returns
    the notebook ID and analysis summary in a single call.
    """
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)

    try:
        # Step 1: Save the uploaded file to a temporary path
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())

        # Step 2: Create the notebook record
        notebook_data = {
            "user_id": str(current_user.id),
            "title": business_problem[:100],
        }
        notebook_response = supabase.table("notebooks").insert(notebook_data).execute()
        new_notebook = notebook_response.data[0]
        notebook_id = new_notebook['id']

        # Step 3: Create a unique path and upload the file to Supabase Storage
        storage_path = f"{current_user.id}/uploads/{uuid.uuid4()}/{file.filename}"
        with open(temp_path, 'rb') as f:
            supabase.storage.from_("mardata-files").upload(
                path=storage_path,
                file=f,
                file_options={"content-type": file.content_type}
            )

        # Step 4: Create the file record in the database
        file_data = {
            "notebook_id": notebook_id,
            "user_id": str(current_user.id),
            "storage_path": storage_path,
            "file_name": file.filename,
            "file_type": file.content_type,
            "file_size_bytes": os.path.getsize(temp_path),
        }
        supabase.table("files").insert(file_data).execute()

        # Step 5: Analyze data and get the analysis summary
        analysis_summary = process_spreadsheet_in_chunks(temp_path, file.filename)
        
        # Step 6: Update the notebook with the analysis cache and data schema
        data_schema = {}
        if isinstance(analysis_summary, dict) and 'all_columns' in analysis_summary:
            for col in analysis_summary['all_columns']:
                if col in analysis_summary.get('numerical_cols', []):
                    data_schema[col] = 'numerical'
                elif col in analysis_summary.get('categorical_cols', []):
                    data_schema[col] = 'categorical'
                else:
                    data_schema[col] = 'unknown'
        
        update_data = {
            "analysis_cache": analysis_summary,
            "data_schema": data_schema,
        }
        supabase.table("notebooks").update(update_data).eq("id", notebook_id).execute()

        # Step 7: Add the AI analysis and Parquet conversion to background tasks
        background_tasks.add_task(
            run_ai_analysis_and_save,
            notebook_id=notebook_id,
            business_problem=business_problem,
            analysis_json=analysis_summary,
            supabase=supabase,
            temp_path=temp_path,
            original_file_name=file.filename,
            user_id=str(current_user.id)
        )

        # Step 8: Return the immediate response
        return {
            "notebook_id": notebook_id,
            "filename": file.filename,
            "analysis_summary": analysis_summary,
            "message": "File processing started.",
        }
    except Exception as e:
        logger.error(f"Error during file upload and processing: {e}")
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            os.rmdir(temp_dir)
        raise HTTPException(status_code=500, detail="An unexpected error occurred during file processing.")
