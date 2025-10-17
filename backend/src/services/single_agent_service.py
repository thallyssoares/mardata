import asyncio
from typing import Dict, Any

from ..lib.llm_models import llm_llama_70b
from . import rag_service
from ..lib.websocket_manager import manager

async def run_single_agent_analysis(business_problem: str, statistical_summary: str, notebook_id: str) -> str:
    """
    Performs data analysis using a single, well-prompted AI agent and streams the results.
    """
    # --- 1. Send initial progress updates ---
    await manager.send_json(notebook_id, {
        "type": "progress",
        "agent": "Expert Data Analyst",
        "status": "Análise iniciada. Interpretando o problema de negócio...",
    })
    await asyncio.sleep(1)

    # --- 2. Retrieve RAG context ---
    await manager.send_json(notebook_id, {
        "type": "progress",
        "agent": "Expert Data Analyst",
        "status": "Consultando base de conhecimento para contexto de mercado...",
    })
    knowledge_context = rag_service.retrieve_knowledge(business_problem)
    await asyncio.sleep(1.5)

    # --- 3. Construct the master prompt ---
    prompt = f"""
    **Você é um Analista de Dados e Estrategista de Negócios sênior. Sua comunicação é direta, concisa e confiante.**

    **Sua Missão:** Resolver o problema de negócio do usuário de forma rápida e acionável, indo direto ao ponto.

    **Diretrizes de Tom e Estilo:**
    - **Seja um Especialista:** Não use linguagem passiva ou neutra. Assuma uma posição e dê recomendações claras.
    - **Seja Conciso:** Seus relatórios devem ser densos em insights, não em palavras. Ajuste o tamanho da sua análise à profundidade dos dados; para dados simples, forneça uma análise curta e objetiva.
    - **Foco na Ação:** Priorize recomendações que o usuário possa implementar imediatamente.

    **Seu Processo:**
    1.  **Análise Direta:** Analise o resumo estatístico e o contexto da base de conhecimento para formar uma hipótese central sobre o problema do usuário.
    2.  **Recomendações Priorizadas:** Crie uma lista de recomendações claras e acionáveis, em ordem de impacto.
    3.  **Relatório Executivo:** Estruture sua análise em um relatório Markdown de fácil leitura. Comece com a conclusão principal.

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

    **RELATÓRIO EXECUTIVO DE ANÁLISE E ESTRATÉGIA (Formato Markdown):**
    """
    await manager.send_json(notebook_id, {
        "type": "progress",
        "agent": "Expert Data Analyst",
        "status": "Todos os dados foram analisados. Gerando o relatório final...",
    })
    await asyncio.sleep(1)

    # --- 4. Invoke LLM and stream the response ---
    response_stream = llm_llama_70b.astream(prompt)
    final_report = ""
    
    # Send the first token to create the message bubble on the frontend
    first_chunk = await anext(response_stream)
    if first_chunk:
        final_report += first_chunk.content
        await manager.send_json(notebook_id, {
            "type": "token",
            "content": first_chunk.content
        })

    # Stream remaining tokens
    async for chunk in response_stream:
        token = chunk.content
        if token:
            final_report += token
            await manager.send_json(notebook_id, {
                "type": "token",
                "content": token
            })
    
    # --- 5. Send stream end message ---
    await manager.send_json(notebook_id, {"type": "stream_end"})

    return final_report
