from . import single_agent_service
from ..lib.llm_models import llm_llama_70b

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
    Você é um assistente de análise de dados especialista. Sua tarefa é responder a perguntas de acompanhamento com base no contexto fornecido.
    Seja direto e conciso. Responda em Português do Brasil.

    **Contexto da Análise Original:**
    {original_analysis}

    **Histórico da Conversa:**
    {history_str}

    **Nova Pergunta do Usuário:**
    "{new_question}"

    **Instruções:**
    1. Responda a pergunta do usuário usando **estritamente** as informações do contexto e do histórico.
    2. Se a informação não estiver disponível, **não diga apenas 'não sei'**. Em vez disso, posicione-se como um especialista e explique **exatamente qual análise adicional seria necessária** para obter a resposta.
    """

    response = llm_llama_70b.invoke(prompt)
    ai_answer = response.content

    return ai_answer