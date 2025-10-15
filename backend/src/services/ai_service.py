
import json
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

    # Serialize the analysis dictionary to a readable string format
    analysis_str = json.dumps(analysis, indent=2, ensure_ascii=False)

    prompt = f"""
    **Role:** You are a world-class data analyst specializing in paid traffic performance.
    **Task:** Analyze the provided data to answer the user's business problem.
    **Constraint:** YOU MUST base your entire analysis STRICTLY on the data summary, statistical analysis, and external knowledge provided below. Do not invent or infer data.

    {knowledge_context}

    **User's Business Problem:** "{business_problem}"

    **Data Context:**
    Here is a complete statistical summary of the data you must use:
    {analysis_str}
    """
    return prompt

def get_ai_insights(analysis: Dict[str, Any], business_problem: str) -> str:
    """
    (Simulated) Generates initial insights by creating a data-driven mock response.
    This proves to the user that their file was read and analyzed.
    """
    # Step 1: Retrieve relevant knowledge from the knowledge base
    retrieved_knowledge = rag_service.retrieve_knowledge(business_problem)

    # Step 2: Generate the prompt with the analysis and retrieved knowledge
    prompt = generate_prompt(analysis, business_problem, retrieved_knowledge)

    # Step 3: Print the prompt for debugging purposes
    print("--- Generated Initial Prompt for AI ---")
    print(prompt)
    print("-------------------------------------")

    # Step 4: Generate a data-driven mock response using reliable analysis data
    try:
        # Use the direct and reliable info from the analysis dictionary
        num_entries = analysis.get('total_records', 'N/A')
        columns = analysis.get('all_columns', [])
        stats = analysis.get('descriptive_stats', {})

        if columns:
            num_cols = len(columns)
            mean_val_str = ""

            # Find the first numeric column to show a sample statistic
            if stats:
                first_numeric_col = list(stats.keys())[0]
                mean_val = stats[first_numeric_col].get('mean', 'N/A')
                if isinstance(mean_val, (int, float)):
                    mean_val = f"{mean_val:.2f}"
                mean_val_str = f"Como um exemplo rápido, a média da coluna '{first_numeric_col}' é de **{mean_val}**. "

            mock_response = (
                f"Análise preliminar do seu arquivo foi concluída com sucesso. "
                f"Identifiquei um total de **{num_entries} registros** e **{num_cols} colunas**. "
                f"As colunas encontradas foram: `{', '.join(columns)}`.\n\n"
                f"{mean_val_str}"
                f"Agora estou pronto para analisar seus dados com base no seu problema: '{business_problem}'"
            )
        else:
            mock_response = (
                "Seu arquivo foi processado, mas não encontrei nenhuma coluna. "
                "Por favor, verifique se o arquivo não está vazio."
            )

    except Exception as e:
        print(f"Error generating data-driven mock response: {e}")
        mock_response = "Ocorreu um erro ao gerar a resposta detalhada, mas seu arquivo foi processado. Verifique os logs do servidor para mais detalhes."

    return mock_response

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
