import json
import pandas as pd
from io import StringIO
from supabase import Client
from . import single_agent_service, code_executor
from ..lib.llm_models import llm_llama_70b
import re # Import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_ai_insights(statistical_summary: str, business_problem: str, notebook_id: str) -> str:
    """
    Uses a single-agent workflow to derive insights from statistical data.
    """
    ai_insights = await single_agent_service.run_single_agent_analysis(
        business_problem=business_problem,
        statistical_summary=statistical_summary,
        notebook_id=notebook_id
    )
    return ai_insights

def build_code_or_text_prompt(chat_history: list, new_question: str, original_analysis: str) -> str:
    history_lines = []
    for msg in chat_history:
        role = "User" if msg.get("role") == "user" else "Assistant"
        history_lines.append(f"{role}: {msg.get('content', '')}")
    history_str = "\n".join(history_lines)

    return f"""
    # SYSTEM PROMPT
    You are a data analysis assistant. Your goal is to answer the user's question based on the provided context.

    **CONTEXT:**
    1.  **Initial Analysis Summary:** A high-level summary of the dataset is available in the `original_analysis` variable.
    2.  **Conversation History:** The ongoing conversation is in `history_str`.

    **YOUR TASK:**
    Based on the user's `new_question`, decide on one of the following two actions:

    1.  **Direct Answer:** If the answer is already available in the conversation history or the initial analysis, provide a direct, concise answer to the user in natural language (Brazilian Portuguese).

    2.  **Code Generation:** If you need to perform a new calculation on the original data (which is available in a pandas DataFrame called `df`), you MUST respond with ONLY a JSON object containing the Python code to be executed. The JSON object must have a single key "code".

    **RULES FOR CODE GENERATION:**
    - The DataFrame is pre-loaded in a variable named `df`.
    - **`pandas` is already imported as `pd`. DO NOT include `import pandas as pd` in your code.**
    - **Prioritize using built-in pandas functions (e.g., .mean(), .sum(), .groupby()) for efficiency and clarity. Avoid re-implementing basic calculations with `.apply()` and `lambda` if a built-in function exists.**
    - Your code will be executed via `exec()`. Use `print()` to output the result.
    - The code must be a single-line or multi-line string inside the JSON object.
    - DO NOT provide any explanation, just the JSON object.

    --- 
    **Initial Analysis Summary:**
    {original_analysis}

    **Conversation History:**
    {history_str}

    **User's New Question:**
    {new_question}
    """

def build_synthesis_prompt(execution_result: str, new_question: str, chat_history: list) -> str:
    history_lines = []
    for msg in chat_history:
        role = "User" if msg.get("role") == "user" else "Assistant"
        history_lines.append(f"{role}: {msg.get('content', '')}")
    history_str = "\n".join(history_lines)

    return f"""
    # SYSTEM PROMPT
    You are a data analysis assistant. Your task is to translate a raw data analysis result into a clear, friendly, and concise answer in Brazilian Portuguese, taking into account the entire conversation history.

    **Context:**
    - Conversation History: {history_str}
    - User's Last Question: "{new_question}"
    - Raw Data Result from Code Execution: {execution_result}

    **Instruction:**
    Formulate a natural language response that directly answers the user's last question, using the provided data and the context of the conversation. Be direct, helpful, and connect your answer to the previous messages if relevant.
    """

def get_follow_up_insight(original_analysis: dict, chat_history: list, new_question: str, file_path: str, supabase_client: Client) -> str:
    """
    Generates a response to a follow-up question, potentially by executing new code.
    """
    # 1. First attempt: Ask the LLM to either answer directly or generate code.
    prompt1 = build_code_or_text_prompt(chat_history, new_question, json.dumps(original_analysis, indent=2))
    llm_response_str = llm_llama_70b.invoke(prompt1).content
    logger.info(f"LLM raw response: {llm_response_str}") # Log raw response

    # Try to extract a JSON block from the LLM's response
    json_start = llm_response_str.find('{')
    json_end = llm_response_str.rfind('}')

    code_to_execute = None
    if json_start != -1 and json_end != -1 and json_end > json_start:
        json_str = llm_response_str[json_start : json_end + 1]
        logger.info(f"Extracted JSON string: {json_str}") # Log extracted JSON
        try:
            response_data = json.loads(json_str)
            code_to_execute = response_data.get("code")
            logger.info(f"Extracted code: {code_to_execute}") # Log extracted code
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to decode JSON from extracted string: {e}")
            pass # Not a valid JSON, treat as natural language

    if code_to_execute:
        # If we got code, execute it
        try:
            # Download the file from Supabase
            logger.info(f"Attempting to download file from Supabase Storage at: {file_path}")
            file_content_response = supabase_client.storage.from_("mardata-files").download(file_path)
            file_content = file_content_response.decode('utf-8')
            
            # TODO: This assumes CSV. Add logic to handle other file types based on file_path extension.
            df = pd.read_csv(StringIO(file_content))

            # Execute the sandboxed code
            execution_result = code_executor.execute_sandboxed_code(df, code_to_execute)

            # 2. Second attempt: Synthesize the result into a natural language answer
            prompt2 = build_synthesis_prompt(execution_result, new_question, chat_history)
            final_answer = llm_llama_70b.invoke(prompt2).content
            return final_answer

        except Exception as e:
            # Handle errors during file download or code execution
            logger.error(f"Unexpected error during file download or code execution: {e}")
            return f"Sorry, I couldn't process that request. Reason: File Download/Execution Error: {e}"
    else:
        # No executable code found, or JSON parsing failed, or no JSON block at all.
        # Treat the entire response as a natural language answer.
        return llm_response_str