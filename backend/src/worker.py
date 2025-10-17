import os
import pandas as pd
from io import StringIO
from dotenv import load_dotenv

from .lib.redis_client import redis_settings
from .lib.supabase_client import get_supabase_client
from .lib.llm_models import llm_llama_70b
from .lib.websocket_manager import manager as websocket_manager

load_dotenv()

# --- Prompt Engineering ---
def build_code_generation_prompt(chat_context: dict, user_question: str) -> str:
    # Safely handle potentially None data_schema
    data_schema = chat_context.get("data_schema") or {}
    schema_str = ", ".join(data_schema.keys())
    
    history_lines = []
    for msg in chat_context.get("chat_history", []):
        role = "User" if msg.get("role") == "user" else "Assistant"
        history_lines.append(f"{role}: {msg.get('content', '')}")
    history_str = "\n".join(history_lines)

    return f"""
# SYSTEM PROMPT
You are a data analysis assistant specializing in Python and Pandas. Your task is to receive a user's question and DataFrame details, and generate ONLY the Python code necessary to answer that question.

**Strict Rules:**
1. The DataFrame is already loaded into the `df` variable.
2. Your code will be executed by an `exec()`. Use `print()` to return the final result.
3. Do not include ANY explanations, just the code.
4. ONLY use the available columns.
5. Return a JSON object containing a key "code" with the code as a string.

**DataFrame Context:**
- Columns: {schema_str}
- Statistical Summary: {chat_context.get("initial_summary", {})}

**Conversation History:**
{history_str}

---
# USER PROMPT
{user_question}
"""

def build_synthesis_prompt(execution_result: str, user_question: str) -> str:
    return f"""
# SYSTEM PROMPT
You are a data analysis assistant. Your task is to translate a raw data analysis result into a clear, friendly, and concise answer in Brazilian Portuguese.

**Context:**
- User's Original Question: "{user_question}"
- Raw Data Result: {execution_result}

**Instruction:**
Formulate a natural language response based on the data provided.
"""

# --- Security-Critical Function ---
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
        from io import StringIO
        import sys
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        exec(code_to_execute, {"__builtins__": {}}, local_vars)

        sys.stdout = old_stdout
        return captured_output.getvalue()
    except Exception as e:
        return f"Error executing code: {e}"

# --- ARQ Worker Task ---
async def process_follow_up_question(ctx, chat_context: dict, user_question: str):
    supabase = ctx["supabase"]
    llm = ctx["llm"]
    notebook_id = chat_context["id"]

    try:
        # 1. Generate Code
        code_gen_prompt = build_code_generation_prompt(chat_context, user_question)
        llm_response = llm.invoke(code_gen_prompt)
        # A simple (and risky) way to parse the JSON from the LLM response string
        code_to_execute = eval(llm_response.content).get("code", "")

        if not code_to_execute:
            raise ValueError("LLM failed to generate valid code.")

        # 2. Download file and execute code
        storage_path = chat_context["original_file_path"]
        file_content_response = supabase.storage.from_("mardata-bucket").download(storage_path)
        file_content = file_content_response.decode('utf-8')
        df = pd.read_csv(StringIO(file_content))
        
        execution_result = execute_sandboxed_code(df, code_to_execute)

        # 3. Synthesize Final Answer
        synthesis_prompt = build_synthesis_prompt(execution_result, user_question)
        final_response_stream = llm.stream(synthesis_prompt)

        # 4. Stream response via WebSocket and collect full response
        full_response = ""
        for chunk in final_response_stream:
            token = chunk.content or ""
            full_response += token
            await websocket_manager.send_json(notebook_id, {"type": "token", "content": token})

        await websocket_manager.send_json(notebook_id, {"type": "stream_end"})

        # 5. Save assistant's message to the database
        supabase.table("messages").insert({
            "notebook_id": notebook_id,
            "role": "assistant",
            "content": full_response
        }).execute()

    except Exception as e:
        error_message = f"Sorry, I couldn't process that request. Reason: {e}"
        await websocket_manager.send_json(notebook_id, {"type": "error", "message": error_message})
        # Optionally, save error to DB as well
        supabase.table("messages").insert({
            "notebook_id": notebook_id,
            "role": "assistant",
            "content": error_message
        }).execute()

# --- ARQ Worker Settings ---
async def on_startup(ctx):
    ctx["supabase"] = get_supabase_client()
    ctx["llm"] = llm_llama_70b

class WorkerSettings:
    functions = [process_follow_up_question]
    on_startup = on_startup
    redis_settings = redis_settings