"""
Service for post-analysis optimizations, such as converting files to Parquet.
"""
import os
import pandas as pd
from supabase import Client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def convert_to_parquet_and_update_record(
    original_file_path: str,
    original_file_name: str,
    notebook_id: str,
    user_id: str,
    supabase: Client
):
    """
    Converts the original uploaded file to Parquet format for faster future access,
    uploads it to storage, and updates the notebook record in the database.

    Args:
        original_file_path: The local path to the originally uploaded file.
        original_file_name: The original name of the uploaded file.
        notebook_id: The ID of the notebook to update.
        user_id: The ID of the user who owns the notebook.
        supabase: An initialized Supabase client instance.
    """
    parquet_path = None
    temp_dir = os.path.dirname(original_file_path)
    try:
        logging.info(f"[Parquet] Starting conversion for notebook {notebook_id}.")
        # 1. Read the original file
        # Since this runs after the initial analysis, we assume the file is valid.
        # We read the whole file for conversion, which is acceptable as a background task.
        if original_file_name.endswith('.csv'):
            df = pd.read_csv(original_file_path)
        elif original_file_name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(original_file_path)
        else:
            logging.warning(f"[Parquet] Unsupported file type for conversion: {original_file_name}")
            return

        # 2. Create a new Parquet file locally
        parquet_filename = "optimized_data.parquet"
        parquet_path = os.path.join(temp_dir, parquet_filename)
        df.to_parquet(parquet_path, engine='pyarrow')
        logging.info(f"[Parquet] Successfully converted file to {parquet_path}.")

        # 3. Upload the new Parquet file to Supabase Storage
        storage_path = f"uploads/{user_id}/{notebook_id}/{parquet_filename}"
        with open(parquet_path, 'rb') as f:
            # The bucket name is 'mardata-files', you may need to create it in Supabase UI
            supabase.storage.from_("mardata-files").upload(path=storage_path, file=f)
        logging.info(f"[Parquet] Successfully uploaded Parquet file to {storage_path}.")

        # 4. Update the database record
        response = supabase.table('notebooks').update({
            'optimized_file_path': storage_path
        }).eq('id', notebook_id).execute()

        if not response.data:
            logging.error(f"[Parquet] Failed to update notebook record for {notebook_id}. No data returned.")
            raise Exception("Failed to update notebook record.")

        logging.info(f"[Parquet] Successfully updated notebook {notebook_id} with optimized file path.")

    except Exception as e:
        logging.error(f"[Parquet] An error occurred during Parquet conversion for notebook {notebook_id}: {e}", exc_info=True)
        # Don't re-raise, as we don't want to crash the main background task if optimization fails.
    finally:
        # 5. Cleanup all local temporary files
        if parquet_path and os.path.exists(parquet_path):
            os.remove(parquet_path)
            logging.info(f"[Parquet] Cleaned up local Parquet file: {parquet_path}")
        if original_file_path and os.path.exists(original_file_path):
            os.remove(original_file_path)
            logging.info(f"[Parquet] Cleaned up original temp file: {original_file_path}")
        if os.path.exists(temp_dir):
            try:
                os.rmdir(temp_dir)
                logging.info(f"[Parquet] Cleaned up temp directory: {temp_dir}")
            except OSError as e:
                logging.error(f"[Parquet] Error removing temp directory {temp_dir}: {e}")
