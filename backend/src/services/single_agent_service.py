import asyncio
from typing import Dict, Any

from ..lib.llm_models import llm_llama_70b
from . import rag_service
from ..lib.websocket_manager import manager

async def run_single_agent_analysis(business_problem: str, statistical_summary: str, notebook_id: str) -> str:
    """
    Performs data analysis using a single, well-prompted AI agent.
    """
    await manager.send_json(notebook_id, {
        "type": "progress",
        "agent": "Expert Data Analyst",
        "status": "Iniciando análise...",
    })

    # 1. Retrieve context from the knowledge base
    await manager.send_json(notebook_id, {
        "type": "progress",
        "agent": "Expert Data Analyst",
        "status": "Consultando base de conhecimento...",
    })
    knowledge_context = rag_service.retrieve_knowledge(business_problem)

    # 2. Construct the master prompt
    prompt = f"""
    **Você é um Analista de Dados e Estrategista de Negócios de elite.**

    **Sua Missão:** Resolver o problema de negócio do usuário de forma direta e acionável, usando os dados fornecidos.

    **Seu Processo:**
    1.  **Entenda o Objetivo:** Restabeleça o problema de negócio do usuário para confirmar o entendimento.
    2.  **Analise os Dados:** Examine o resumo estatístico fornecido. Identifique as principais alavancas, correlações e anomalias.
    3.  **Incorpore o Contexto:** Utilize o contexto da base de conhecimento para qualificar suas descobertas (ex: se um CPC é alto ou baixo para o setor).
    4.  **Formule uma Hipótese Central:** Crie uma hipótese clara que explique o cenário atual.
    5.  **Desenvolva Recomendações Estratégicas:** Crie uma lista de recomendações claras, priorizadas e acionáveis que o usuário pode implementar imediatamente para atingir seu objetivo.
    6.  **Estruture o Relatório Final:** Apresente sua análise em um relatório Markdown claro e bem estruturado.

    --- 

    **PROBLEMA DE NEGÓCIO DO USUÁRIO:**
    "{business_problem}"

    **RESUMO ESTATÍSTICO DOS DADOS:**
    ```json
    {statistical_summary}
    ```

    **CONTEXTO DA BASE DE CONHECIMENTO (RAG):**
    {knowledge_context}

    ---

    **RELATÓRIO FINAL DE ANÁLISE E ESTRATÉGIA (Formato Markdown):**
    """

    # 3. Invoke the LLM
    await manager.send_json(notebook_id, {
        "type": "progress",
        "agent": "Expert Data Analyst",
        "status": "Gerando insights...",
    })

    response = await llm_llama_70b.ainvoke(prompt)
    final_report = response.content

    # 4. Send the final message
    final_message = {
        "type": "complete",
        "final_insight": final_report
    }
    await manager.send_json(notebook_id, final_message)

    return final_report
