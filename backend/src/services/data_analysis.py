
import pandas as pd
from typing import Dict, Any

def generate_descriptive_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generates a dictionary of descriptive statistics for a given DataFrame.

    This analysis will be used to build the context for the AI model.

    Args:
        df: The cleaned pandas DataFrame.

    Returns:
        A dictionary containing various statistical summaries.
    """
    analysis_output = {}

    # Add direct, reliable information about the DataFrame
    analysis_output['total_records'] = len(df)
    analysis_output['all_columns'] = df.columns.tolist()

    # 1. Basic Info (dtypes, non-null counts)
    # Using a string buffer to capture the output of df.info()
    import io
    buffer = io.StringIO()
    df.info(buf=buffer)
    analysis_output['dataframe_info'] = buffer.getvalue()

    # 2. Descriptive Statistics for numerical columns
    # to_dict() converts the resulting DataFrame into a dictionary
    analysis_output['descriptive_stats'] = df.describe().to_dict()

    # 3. Correlation Matrix for numerical columns
    # We only compute this if there are at least 2 numerical columns
    numerical_cols = df.select_dtypes(include=['number']).columns
    if len(numerical_cols) > 1:
        analysis_output['correlation_matrix'] = df[numerical_cols].corr().to_dict()
    else:
        analysis_output['correlation_matrix'] = "Not enough numerical columns to compute correlation."

    # 4. Value counts for categorical columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    value_counts = {}
    for col in categorical_cols:
        # Limit to the top 20 most frequent values for brevity
        value_counts[col] = df[col].value_counts().nlargest(20).to_dict()
    analysis_output['value_counts'] = value_counts

    # 5. Missing values summary
    missing_values = df.isnull().sum()
    analysis_output['missing_values'] = missing_values[missing_values > 0].to_dict()

    return analysis_output
