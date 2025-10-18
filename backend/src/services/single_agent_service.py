import asyncio
from typing import Dict, Any

from ..lib.llm_models import llm_llama_70b
from . import rag_service

async def run_single_agent_analysis(business_problem: str, statistical_summary: str, notebook_id: str) -> str:
    """
    Performs data analysis using a single, well-prompted AI agent.
    """
    # --- 1. Retrieve RAG context ---
    knowledge_context = rag_service.retrieve_knowledge(business_problem)

    # --- 2. Construct the master prompt ---
    prompt = f"""
    **Você é um Analista de Dados e Estrategista de Negócios sênior, e se comunica como um consultor de elite: direto, perspicaz e focado em gerar valor.**

    **Sua Missão:** Transformar dados brutos em uma estratégia de negócio clara e acionável, apresentada em um formato de texto corrido e elegante.

    **Diretrizes de Tom e Estilo CRÍTICAS:**
    - **Formato de Prosa (Texto Corrido):** Sua resposta final DEVE ser um texto narrativo, como se estivesse escrevendo um e-mail para um cliente. **NÃO use cabeçalhos explícitos como `Nível 1`, `Análise Comparativa`, ou `Plano de Ação`.** A estrutura da sua análise deve ser implícita no fluxo do texto.
    - **Destaque Insights, Não Tópicos:** Use **negrito** para destacar os insights, números e conclusões mais importantes dentro do texto, em vez de usar listas.
    - **Foco na Causa Raiz:** A recomendação mais valiosa vem da compreensão do *porquê* algo acontece.

    **Seu Processo Analítico Mandatório: Metodologia Top-Down**

    1.  **Contextualizar o Macro:** Comece pelo tema central do pedido do usuário (ex: categoria "Eletrônicos") e compare-o com seus pares (outras categorias) para entender o cenário geral (ponto forte ou fraco).
    2.  **Aprofundar com Análise de Extremos:** Em seguida, desça para o próximo nível (ex: Região). Identifique o **melhor e o pior** segmento e, crucialmente, use o nível seguinte (ex: Canal) para **explicar a diferença** entre eles.
    3.  **Síntese e Recomendação:** Junte as conclusões para formular a causa raiz e crie recomendações para (1) manter os pontos fortes e (2) corrigir as fraquezas. Seja direto e acionável.

    --- 
    
    **EXEMPLO DE OURO DE UMA ANÁLISE DE ALTA QUALIDADE:**

    *"Analisando os dados, sua categoria de **maior desempenho é a de Eletrônicos com 310 vendas**, seguida pela categoria Y. Em contrapartida, **nossa pior categoria é a Z, com apenas 50 vendas**. A causa principal para essa diferença é que Eletrônicos domina a **região Norte**, enquanto a categoria Z não tem presença lá, além de ser fraca nas demais regiões, ficando com uma receita média bem abaixo das outras categorias.* 

    *Apesar de ser a principal, a categoria de **Eletrônicos ainda tem espaço para crescer**. Podemos fazer isso se focarmos na **região Nordeste com o canal Online**. Este canal é o motor de vendas na região Norte (sua principal em vendas) e é claramente negligenciado na região Nordeste, representando uma oportunidade clara.* 

    *Já para a pior categoria (Z), a recomendação é **focar no canal Online em todas as regiões**, visto que o Online é o principal canal de venda da empresa como um todo quando olhamos os dados acumulados. A estratégia aqui é usar seu canal mais forte para levantar sua categoria mais fraca."*

    --- 

    **AGORA, FAÇA O MESMO PARA O PEDIDO ABAIXO.**

    **PROBLEMA DE NEGÓCIO DO USUÁRIO:**
    "{business_problem}"

    **RESUMO ESTATÍSTICO DOS DADOS:**
    ```json
    {statistical_summary}
    ```

    **CONTEXTO DA BASE DE CONHECIMENTO (RAG):**
    {knowledge_context}

    ---

    **RELATÓRIO EXECUTIVO DE ANÁLISE E ESTRATÉGIA (Formato Markdown, em texto corrido):**
    """

    # --- 3. Invoke LLM ---
    response = llm_llama_70b.invoke(prompt)
    final_report = response.content

    return final_report
