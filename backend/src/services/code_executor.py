import pandas as pd
from io import StringIO

def execute_sandboxed_code(df: pd.DataFrame, code_to_execute: str) -> str:
    """
    Executes the LLM-generated code in a restricted environment.

    **WARNING: THIS IS A MAJOR SECURITY RISK.** In a real-world scenario, this `exec`
    should be replaced with a proper sandboxing library (e.g., RestrictedPython)
    or run inside an isolated Docker container.
    """
    local_vars = {"df": df, "pd": pd}
    try:
        # Redirect stdout to capture the print() output from the executed code
        
        old_stdout = __import__("sys").stdout
        __import__("sys").stdout = captured_output = StringIO()

        exec(code_to_execute, {"__builtins__": {}}, local_vars)

        __import__("sys").stdout = old_stdout
        return captured_output.getvalue()
    except Exception as e:
        return f"Error executing code: {e}"
