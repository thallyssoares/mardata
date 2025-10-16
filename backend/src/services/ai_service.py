from . import crew_service
from ..lib.llm_models import llm_llama_70b

async def get_ai_insights(statistical_summary: str, business_problem: str, notebook_id: str) -> str:
    """
    Uses the CrewAI agentic workflow to derive insights from statistical data.
    """
    ai_insights = await crew_service.run_analysis(
        user_prompt=business_problem,
        statistical_summary=statistical_summary,
        notebook_id=notebook_id
    )
    return ai_insights

def get_follow_up_insight(original_analysis: str, chat_history: list, new_question: str) -> str:
    """
    Generates a response to a follow-up question using an AI model,
    based on the initial analysis and conversation history.
    """
    history_lines = []
    for msg in chat_history:
        if msg.get('role') == 'user':
            history_lines.append(f"Usuário: {msg.get('content', '')}")
        elif msg.get('role') == 'assistant':
            history_lines.append(f"Assistente: {msg.get('content', '')}")
    history_str = "\n".join(history_lines)

    prompt = f"""
    Você é um assistente de análise de dados. Sua única tarefa é responder a perguntas de acompanhamento com base estritamente no contexto fornecido.
    Responda em Português do Brasil.

    **Contexto da Análise Original:**
    {original_analysis}

    **Histórico da Conversa:**
    {history_str}

    **Nova Pergunta do Usuário:**
    "{new_question}"

    Baseado SOMENTE no contexto e no histórico, responda à nova pergunta.
    """

    response = llm_llama_70b.invoke(prompt)
    ai_answer = response.content

    return ai_answer