
import pandas as pd
from fastapi import UploadFile
import io

def _infer_csv_options(sample_bytes: bytes) -> dict:
    """
    Infers decimal and thousands separators for a CSV file from a sample.

    Args:
        sample_bytes: A small binary sample (e.g., first 2KB) of the CSV file.

    Returns:
        A dictionary with 'decimal' and 'thousands' keys for pandas.read_csv.
    """
    sample_str = sample_bytes.decode(errors='ignore')

    # Heuristic: In many non-US formats (like Brazilian Portuguese), the comma
    # is the decimal separator and the period is for thousands (e.g., "1.234,56").
    # In US/UK format, it's "1,234.56". We check which character appears.
    # A simple count can be a decent indicator.
    if sample_str.count(',') > sample_str.count('.'):
        return {'decimal': ',', 'thousands': '.'}
    
    return {'decimal': '.', 'thousands': ','}


def clean_data(file: UploadFile) -> pd.DataFrame:
    """
    Reads an uploaded file, cleans the data, and returns a pandas DataFrame.
    It automatically detects the decimal separator for CSV files.

    Args:
        file: The uploaded file from the FastAPI request.

    Returns:
        A cleaned pandas DataFrame.
    """
    try:
        # Read the file content into a BytesIO object
        content = file.file.read()
        file.file.seek(0)  # Reset file pointer

        # Detect file type and read with pandas
        if file.filename.endswith('.csv'):
            # Infer separators from a sample of the file
            options = _infer_csv_options(content[:2048]) # Use first 2KB for sniffing
            df = pd.read_csv(io.BytesIO(content), decimal=options['decimal'], thousands=options['thousands'])
        elif file.filename.endswith(('.xls', '.xlsx')):
            # read_excel is generally better at handling this automatically
            df = pd.read_excel(io.BytesIO(content))
        else:
            # For simplicity, we'll raise an error for unsupported file types.
            raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")

        # --- Basic Data Cleaning Steps ---
        # 1. Handle missing values (example: fill with 0, or drop)
        # This is a placeholder. Actual strategy will depend on the data.
        df.fillna(0, inplace=True)

        # 2. Remove duplicate rows
        df.drop_duplicates(inplace=True)

        # 3. TODO: Add more specific cleaning logic based on expected data patterns.
        # (e.g., convert data types, standardize column names, etc.)

        return df

    except Exception as e:
        # In a real application, you'd want more robust error handling and logging.
        print(f"Error processing file {file.filename}: {e}")
        raise
