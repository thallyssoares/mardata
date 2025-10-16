import json
from typing import Dict, Any, List
from . import rag_service
from . import crew_service

def get_ai_insights(analysis: Dict[str, Any], business_problem: str) -> str:
    """
    Generates insights by running the CrewAI analysis.
    """
    # Convert the analysis dictionary to a string for the prompt
    statistical_summary = json.dumps(analysis, indent=2, ensure_ascii=False)

    # Run the crew analysis
    result = crew_service.run_analysis(business_problem, statistical_summary)

    return result

def generate_follow_up_prompt(
    original_analysis: Dict[str, Any],
    chat_history: List[Dict[str, str]],
    new_question: str
) -> str:
    """
    Generates a prompt for a follow-up question.
    """
    # Correctly build the history string based on the {'role': ..., 'content': ...} structure
    history_lines = []
    for msg in chat_history:
        if msg['role'] == 'user':
            history_lines.append(f"User: {msg['content']}")
        elif msg['role'] == 'assistant':
            history_lines.append(f"AI: {msg['content']}")
    history_str = "\n".join(history_lines)

    analysis_str = json.dumps(original_analysis, indent=2, ensure_ascii=False)

    prompt = f"""
    **Role:** You are a world-class data analyst continuing a conversation.
    **Constraint:** You MUST answer the new question based ONLY on the original data context provided. Do not use outside knowledge unless it was in the original prompt.

    **Original Data Context:**
    {analysis_str}

    **Conversation History:**
    {history_str}

    **New User Question:** \"{new_question}\"\n
    **Task:** Answer the new question based on the original data and the conversation history.
    """
    return prompt

def get_follow_up_insight(
    original_analysis: Dict[str, Any],
    chat_history: List[Dict[str, str]],
    new_question: str
) -> str:
    """
    (Simulated) Generates a response to a follow-up question.
    """
    prompt = generate_follow_up_prompt(original_analysis, chat_history, new_question)

    print("--- Generated Follow-up Prompt for AI ---")
    print(prompt)
    print("---------------------------------------")

    # Mock response for a follow-up question
    return "Based on the original data, the day with the worst CPA was Wednesday."