
from typing import Dict, Any, List
from . import rag_service

def generate_prompt(
    analysis: Dict[str, Any],
    business_problem: str,
    retrieved_knowledge: str = ""
) -> str:
    """
    Generates a detailed, structured prompt for the AI model.
    """
    knowledge_context = ""
    if retrieved_knowledge:
        knowledge_context = f"""
        **External Knowledge Context (RAG):**
        To help you reason about the data, here is some relevant information about common paid traffic metrics:
        {retrieved_knowledge}
        """

    prompt = f"""
    **Role:** You are a world-class data analyst specializing in paid traffic performance.
    **Task:** Analyze the provided data to answer the user's business problem.
    **Constraint:** YOU MUST base your entire analysis STRICTLY on the data summary, statistical analysis, and external knowledge provided below. Do not invent or infer data.

    {knowledge_context}

    **User's Business Problem:** "{business_problem}"

    **Data Context:**
    Here is a complete statistical summary of the data you must use:
    ...
    """ # The rest of the prompt remains the same as before
    return prompt

def get_ai_insights(analysis: Dict[str, Any], business_problem: str) -> str:
    """
    (Simulated) Generates initial insights by retrieving knowledge (RAG) and calling an AI model.
    """
    # Step 1: Retrieve relevant knowledge from the knowledge base
    retrieved_knowledge = rag_service.retrieve_knowledge(business_problem)

    # Step 2: Generate the prompt with the retrieved knowledge
    prompt = generate_prompt(analysis, business_problem, retrieved_knowledge)

    # Step 3: (Mock) Call the AI API
    print("--- Generated Initial Prompt for AI ---")
    print(prompt)
    print("-------------------------------------")

    mock_response = """...""" # Mock response remains the same
    return mock_response

def generate_follow_up_prompt(
    original_analysis: Dict[str, Any],
    chat_history: List[Dict[str, str]],
    new_question: str
) -> str:
    """
    Generates a prompt for a follow-up question.
    """
    history_str = "\n".join([f"User: {msg['user']}\nAI: {msg['ai']}" for msg in chat_history])

    prompt = f"""
    **Role:** You are a world-class data analyst continuing a conversation.
    **Constraint:** You MUST answer the new question based ONLY on the original data context provided. Do not use outside knowledge unless it was in the original prompt.

    **Original Data Context:**
    {original_analysis}

    **Conversation History:**
    {history_str}

    **New User Question:** "{new_question}"

    **Task:** Answer the new question based on the original data and the conversation history.
    """
    return prompt

def get_follow_up_insight(original_analysis: Dict[str, Any], chat_history: List[Dict[str, str]], new_question: str) -> str:
    """
    (Simulated) Generates a response to a follow-up question.
    """
    prompt = generate_follow_up_prompt(original_analysis, chat_history, new_question)

    print("--- Generated Follow-up Prompt for AI ---")
    print(prompt)
    print("---------------------------------------")

    # Mock response for a follow-up question
    return "Based on the original data, the day with the worst CPA was Wednesday."
