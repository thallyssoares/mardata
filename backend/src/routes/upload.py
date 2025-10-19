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
from ..lib.supabase_client import get_supabase_client, supabase_url
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


@router.post("/upload/presigned-url/")
async def create_presigned_url(
    business_problem: str = Form(...),
    file_name: str = Form(...),
    file_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Creates a notebook, generates a presigned URL for file upload,
    and returns the URL and notebook ID to the client.
    """
    try:
        # Step 1: Create a unique path for the file in storage
        storage_path = f"{current_user.id}/uploads/{uuid.uuid4()}/{file_name}"
        
        # Step 2: Generate a presigned URL from Supabase Storage
        presigned_url_response = supabase.storage.from_("mardata-files").create_signed_upload_url(
            path=storage_path
        )
        
        # The response from Supabase is a relative URL, so we need to construct the full URL
        absolute_presigned_url = f"{supabase_url}/{presigned_url_response['signed_url']}"

        # Step 3: Create the notebook record in the database
        notebook_data = {
            "user_id": str(current_user.id),
            "title": business_problem[:100],
        }
        notebook_response = supabase.table("notebooks").insert(notebook_data).execute()
        new_notebook = notebook_response.data[0]
        notebook_id = new_notebook['id']

        # Step 4: Create the file record associated with the notebook
        file_data = {
            "notebook_id": notebook_id,
            "user_id": str(current_user.id),
            "storage_path": storage_path,
            "file_name": file_name,
            "file_type": file_type,
        }
        supabase.table("files").insert(file_data).execute()

        # Step 5: Return the absolute presigned URL and notebook ID
        return {
            "presigned_url": absolute_presigned_url,
            "storage_path": storage_path,
            "notebook_id": notebook_id,
        }
    except Exception as e:
        logger.error(f"Error creating presigned URL: {e}")
        raise HTTPException(status_code=500, detail="Could not create presigned URL.")


@router.post("/process-upload/")
async def process_uploaded_file(
    background_tasks: BackgroundTasks,
    notebook_id: str = Form(...),
    business_problem: str = Form(...),
    file_name: str = Form(...),
    storage_path: str = Form(...),
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    After the file is uploaded to storage, this endpoint triggers the analysis
    and optimization in the background.
    """
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file_name)

    try:
        # Step 1: Download the file from storage to a temporary path
        with open(temp_path, 'wb') as f:
            res = supabase.storage.from_("mardata-files").download(storage_path)
            f.write(res)

        # Step 2: Analyze data and get the analysis summary
        analysis_summary = process_spreadsheet_in_chunks(temp_path, file_name)
        
        # Step 3: Update the notebook with the analysis cache and data schema
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
        supabase.table("notebooks").update(update_data).eq("id", notebook_id).eq("user_id", str(current_user.id)).execute()
        
        # Step 4: Get file size and update the file record
        file_size_bytes = os.path.getsize(temp_path)
        supabase.table("files").update({"file_size_bytes": file_size_bytes}).eq("storage_path", storage_path).eq("user_id", str(current_user.id)).execute()

        # Step 5: Add the AI analysis and Parquet conversion to background tasks
        background_tasks.add_task(
            run_ai_analysis_and_save,
            notebook_id=notebook_id,
            business_problem=business_problem,
            analysis_json=analysis_summary,
            supabase=supabase,
            temp_path=temp_path,
            original_file_name=file_name,
            user_id=str(current_user.id)
        )

        # Step 6: Return the immediate response
        return {
            "notebook_id": notebook_id,
            "filename": file_name,
            "analysis_summary": analysis_summary,
            "message": "File processing started.",
        }
    except Exception as e:
        logger.error(f"Error processing uploaded file: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
            os.rmdir(temp_dir)
        raise HTTPException(status_code=500, detail="An unexpected error occurred during file processing.")
