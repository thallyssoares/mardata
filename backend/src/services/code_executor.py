import pandas as pd
from io import StringIO
import logging

logger = logging.getLogger(__name__)

def execute_sandboxed_code(df: pd.DataFrame, code_to_execute: str) -> str:
    """
    Executes the LLM-generated code in a restricted environment.

    **WARNING: THIS IS A MAJOR SECURITY RISK.** In a real-world scenario, this `exec`
    should be replaced with a proper sandboxing library (e.g., RestrictedPython)
    or run inside an isolated Docker container.
    """
    local_vars = {"df": df, "pd": pd}

    # A safe subset of built-in functions
    safe_builtins = {
        "print": print,
        "len": len,
        "sum": sum,
        "dict": dict,
        "list": list,
        "str": str,
        "int": int,
        "float": float,
        "range": range,
        "zip": zip,
        "enumerate": enumerate,
        "map": map,
        "filter": filter,
        "sorted": sorted,
        "min": min,
        "max": max,
        "abs": abs,
        "round": round,
        "pow": pow,
        "all": all,
        "any": any,
        "isinstance": isinstance,
        "hasattr": hasattr,
        "getattr": getattr,
        "setattr": setattr,
        "delattr": delattr,
        "dir": dir,
        "help": help,
        "id": id,
        "repr": repr,
        "callable": callable,
        "type": type,
        "vars": vars,
        "globals": globals,
        "locals": locals,
    }

    try:
        # Redirect stdout to capture the print() output from the executed code
        
        old_stdout = __import__("sys").stdout
        __import__("sys").stdout = captured_output = StringIO()

        exec(code_to_execute, {"__builtins__": safe_builtins}, local_vars)

        __import__("sys").stdout = old_stdout
        result = captured_output.getvalue()
        logger.info(f"Executed code output: {result}")
        return result
    except Exception as e:
        logger.error(f"Error executing code: {e}")
        return f"Error executing code: {e}"
