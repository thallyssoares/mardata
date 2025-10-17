"""
Service for processing large spreadsheet files in chunks to conserve memory.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from collections import Counter
import io

def _convert_numpy_types(obj):
    """Recursively converts numpy number types to native Python types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: _convert_numpy_types(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_numpy_types(i) for i in obj]
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def _infer_csv_options(file_path: str) -> dict:
    """
    Infers decimal and thousands separators for a CSV file from a sample.

    Args:
        file_path: The path to the CSV file.

    Returns:
        A dictionary with 'decimal' and 'thousands' keys for pandas.read_csv.
    """
    with open(file_path, 'rb') as f:
        sample_bytes = f.read(2048)
    
    sample_str = sample_bytes.decode(errors='ignore')
    if sample_str.count(',') > sample_str.count('.'):
        return {'decimal': ',', 'thousands': '.'}
    
    return {'decimal': '.', 'thousands': ','}

def process_spreadsheet_in_chunks(file_path: str, file_name: str) -> Dict[str, Any]:
    """
    Reads and analyzes a spreadsheet in chunks to keep memory usage low.

    This function is designed primarily for large CSV files. For other formats,
    it may fall back to in-memory processing if chunking is not supported.

    Args:
        file_path: The local path to the spreadsheet file.
        file_name: The original name of the file to determine its type.

    Returns:
        A dictionary containing the consolidated statistical summary.
    """
    if not file_name.endswith('.csv'):
        # Fallback for non-CSV files like Excel, processing them in-memory for now.
        # This maintains previous functionality for other file types.
        df = pd.read_excel(file_path) if file_name.endswith(('.xls', '.xlsx')) else pd.read_csv(file_path)
        df.fillna(0, inplace=True)
        df.drop_duplicates(inplace=True)
        # This part will be memory intensive for large non-csv files.
        # The user story is focused on CSV, so this is an acceptable trade-off.
        from .data_analysis import generate_descriptive_analysis
        return generate_descriptive_analysis(df)

    # --- Chunked Processing for CSV files ---
    options = _infer_csv_options(file_path)
    chunk_iterator = pd.read_csv(
        file_path,
        chunksize=50000,
        decimal=options['decimal'],
        thousands=options['thousands']
    )

    total_records = 0
    all_columns = []
    categorical_cols = []
    numerical_cols = []
    value_counters = {}
    missing_values_counter = Counter()
    
    # Data for descriptive stats
    descriptive_stats_agg = {}

    is_first_chunk = True
    for chunk in chunk_iterator:
        chunk.fillna(0, inplace=True)
        chunk.drop_duplicates(inplace=True)

        if is_first_chunk:
            all_columns = chunk.columns.tolist()
            numerical_cols = chunk.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = chunk.select_dtypes(include=['object', 'category']).columns.tolist()
            
            for col in categorical_cols:
                value_counters[col] = Counter()
            for col in numerical_cols:
                # [count, sum, min, max]
                descriptive_stats_agg[col] = [0, 0, float('inf'), float('-inf')]

            is_first_chunk = False

        total_records += len(chunk)
        missing_values_counter.update(chunk.isnull().sum().to_dict())

        # Aggregate value counts for categorical columns
        for col in categorical_cols:
            value_counters[col].update(chunk[col].value_counts().to_dict())

        # Aggregate descriptive stats for numerical columns
        for col in numerical_cols:
            stats = descriptive_stats_agg[col]
            stats[0] += chunk[col].count()
            stats[1] += chunk[col].sum()
            stats[2] = min(stats[2], chunk[col].min())
            stats[3] = max(stats[3], chunk[col].max())

    # --- Consolidate Results ---
    final_analysis = {}
    final_analysis['total_records'] = total_records
    final_analysis['all_columns'] = all_columns
    
    # Consolidate value counts
    final_value_counts = {}
    for col, counter in value_counters.items():
        final_value_counts[col] = dict(counter.most_common(20))
    final_analysis['value_counts'] = final_value_counts

    # Consolidate missing values
    final_analysis['missing_values'] = {k: v for k, v in missing_values_counter.items() if v > 0}

    # Consolidate and calculate descriptive stats
    final_descriptive_stats = {}
    for col, (count, total_sum, min_val, max_val) in descriptive_stats_agg.items():
        mean = total_sum / count if count > 0 else 0
        final_descriptive_stats[col] = {
            'count': count,
            'mean': mean,
            'std': 'N/A (Chunked Processing)', # Std dev is complex to calculate in chunks
            'min': min_val if min_val != float('inf') else 0,
            '25%': 'N/A (Chunked Processing)',
            '50%': 'N/A (Chunked Processing)',
            '75%': 'N/A (Chunked Processing)',
            'max': max_val if max_val != float('-inf') else 0,
        }
    final_analysis['descriptive_stats'] = final_descriptive_stats
    
    # Add placeholders for stats that are too complex for chunking
    final_analysis['dataframe_info'] = f"""<class 'pandas.core.frame.DataFrame'>
RangeIndex: {total_records} entries
Data columns (total {len(all_columns)} columns):
(Column info is not available in chunked processing mode)
"""
    final_analysis['correlation_matrix'] = "Not available in chunked processing mode."

    # Convert all numpy types to native Python types for JSON serialization
    return _convert_numpy_types(final_analysis)
