
-----

# PRD: Análise Interativa Pós-Processamento (Chat Contínuo)

**Autor:** [Seu Nome]
**Data:** 17/10/2025
**Versão:** 1.0

## 1\. Visão Geral e Objetivo

### 1.1. Resumo da Funcionalidade (O quê?)

Esta funcionalidade implementa a capacidade de os usuários continuarem a conversa com a IA em chats de análise já existentes. Após a geração do relatório inicial, o usuário poderá fazer perguntas de acompanhamento e a IA irá consultar os dados da planilha original para fornecer respostas precisas e em tempo real, sem a necessidade de um novo upload ou reprocessamento completo.

### 1.2. Problema a Ser Resolvido (Por quê?)

Atualmente, a análise do MarData é um processo de "via única". O usuário envia os dados, recebe um relatório e a interação termina. Se surgirem novas dúvidas, o usuário precisa iniciar um novo processo, o que é ineficiente e frustrante. Isso quebra o fluxo de análise e limita o valor da plataforma, transformando-a em um gerador de relatórios estáticos em vez de uma ferramenta de exploração de dados dinâmica.

### 1.3. Objetivos e Critérios de Sucesso

  * **Objetivo Principal:** Transformar cada chat em um ambiente de análise de dados persistente e interativo.
  * **Critério de Sucesso 1 (Engajamento):** Aumento de 30% no número de mensagens trocadas por sessão de análise após a implementação.
  * **Critério de Sucesso 2 (Retenção):** Usuários do Free-Tier retornam para interagir com chats antigos pelo menos 2 vezes por semana.
  * **Critério de Sucesso 3 (Performance):** O tempo de resposta para perguntas de acompanhamento deve ser, em média, inferior a 10 segundos.

## 2\. Requisitos Funcionais e Fluxo de Uso

### 2.1. Escopo (O que está incluído no MVP)

  * O usuário pode abrir qualquer chat concluído em seu dashboard.
  * A caixa de texto para novas mensagens estará ativa nesses chats.
  * O usuário pode fazer perguntas abertas sobre os dados da planilha originalmente enviada.
  * A IA deve responder estritamente com base nos dados contidos na planilha.
  * O histórico da nova conversa é salvo e anexado ao chat existente.

### 2.2. Fluxo do Usuário

1.  O usuário faz login e acessa seu Dashboard.
2.  Ele clica em um "Notebook" (chat) que já possui uma análise concluída.
3.  A tela de chat é exibida com o histórico completo da análise inicial. A caixa de texto está habilitada.
4.  O usuário digita uma nova pergunta, como: `"Filtre apenas a Campanha X e me diga qual foi o Custo por Clique (CPC) médio dela."` e envia.
5.  A interface exibe um indicador de que a IA está "pensando...".
6.  Em segundos, a resposta da IA aparece na tela, em streaming, como se estivesse sendo digitada em tempo real. Ex: `"Claro! O Custo por Clique (CPC) médio para a Campanha X foi de R$ 2,50."`

### 2.3. Requisitos da Interface (UI/UX)

  * Nenhuma mudança drástica na UI é necessária. A principal alteração é manter o componente de input de texto (`Textarea` e `Button`) habilitado após a análise inicial.
  * Um estado de `loading` claro deve ser exibido na mensagem da IA enquanto a resposta está sendo processada no backend.

## 3\. Especificações Técnicas e Arquitetura

A estratégia central é capacitar a LLM a gerar código Python (Pandas) sob demanda para responder às perguntas, que será executado pelo nosso backend.

### 3.1. Modificações no Modelo de Dados (Supabase/PostgreSQL)

A tabela `chats` (ou `notebooks`) precisará de novos campos para armazenar o contexto de cada análise:

```sql
-- Exemplo de alteração na tabela 'chats'
ALTER TABLE chats
ADD COLUMN original_file_path TEXT,      -- Caminho para o arquivo no Supabase Storage
ADD COLUMN data_schema JSONB,            -- Nomes das colunas e tipos de dados (ex: {"Nome": "text", "Custo": "numeric"})
ADD COLUMN initial_summary JSONB;        -- O df.describe() e outras estatísticas iniciais
```

O `chat_history` (que provavelmente já existe) continuará sendo usado.

### 3.2. Fluxo do Sistema (Backend - FastAPI)

1.  **Requisição:** O Frontend envia um `POST` para `/chats/{chat_id}/message` com o corpo `{"content": "nova pergunta do usuário"}`.
2.  **Recuperação de Contexto:** O endpoint busca no banco de dados todas as informações associadas ao `chat_id`: `original_file_path`, `data_schema`, `chat_history`.
3.  **Enfileiramento:** A tarefa é enfileirada no Redis (via ARQ) para um worker, passando o contexto recuperado e a nova pergunta. A API retorna `202 Accepted` imediatamente.
4.  **Worker - Passo 1 (Geração de Código):**
      * O worker constrói um "meta-prompt" para a LLM.
      * A LLM é instruída a agir como um "analista de dados que gera código" e retorna um JSON com o código Pandas necessário para responder à pergunta.
5.  **Worker - Passo 2 (Execução Segura):**
      * O worker baixa a planilha do Supabase Storage.
      * Carrega a planilha em um DataFrame Pandas.
      * **Executa o código gerado pela LLM em um ambiente seguro e isolado.**
      * Captura o resultado da execução (ex: um valor, uma lista, um pequeno DataFrame em JSON).
6.  **Worker - Passo 3 (Síntese da Resposta):**
      * O worker faz uma segunda chamada (muito mais simples) à LLM.
      * Ele envia o resultado da execução e pede para a IA formular uma resposta amigável em linguagem natural.
7.  **Streaming da Resposta:** O worker envia a resposta final, token por token, via WebSocket para o frontend.
8.  **Persistência:** O worker atualiza o campo `chat_history` no banco de dados com a nova pergunta e a resposta final.

### 3.3. Engenharia de Prompt: O Coração da Funcionalidade

Esta é a implementação do "agente de código" sem um sistema complexo. Tudo reside na instrução dada à LLM.

**Exemplo de Prompt para Geração de Código (Worker - Passo 1):**

```text
# SYSTEM PROMPT
Você é um assistente de análise de dados especialista em Python e Pandas. Sua tarefa é receber uma pergunta do usuário e os detalhes de um DataFrame, e gerar APENAS o código Python necessário para responder a essa pergunta.

**Regras Estritas:**
1. O DataFrame já estará carregado na variável `df`.
2. Seu código será executado por um `exec()`. Use `print()` para retornar o resultado final.
3. Não inclua NENHUMA explicação, apenas o código.
4. Use APENAS as colunas disponíveis.
5. Retorne um objeto JSON contendo uma chave "code" com o código como uma string.

**Contexto do DataFrame:**
- Schema: {{data_schema}}
- Resumo Estatístico: {{initial_summary}}

**Histórico da Conversa:**
{{chat_history}}

---
# USER PROMPT
{{new_user_question}}
```

### 3.4. Exemplos de Código

**Endpoint FastAPI (Simplificado):**

```python
# app/routers/chats.py

from fastapi import APIRouter, Depends
from arq.connections import ArqRedis

from app.schemas import NewMessage
from app.dependencies import get_redis, get_current_user

router = APIRouter()

@router.post("/chats/{chat_id}/message")
async def post_message(
    chat_id: str,
    message: NewMessage,
    user: dict = Depends(get_current_user),
    redis: ArqRedis = Depends(get_redis)
):
    # 1. Buscar contexto do chat_id no Supabase (verificar se o 'user' tem permissão)
    chat_context = await db.get_chat_context(chat_id, user["id"])

    # 2. Enfileirar a tarefa no ARQ (Redis)
    await redis.enqueue_job(
        "process_follow_up_question",
        chat_context,
        message.content
    )
    return {"status": "processing"}
```

**Worker ARQ (Simplificado):**

```python
# app/workers.py

import pandas as pd
from io import StringIO

# Função que será executada pelo worker
async def process_follow_up_question(ctx, chat_context: dict, user_question: str):
    redis = ctx["redis"]
    
    # 1. Construir o prompt e chamar a LLM para gerar o código
    prompt = build_code_generation_prompt(chat_context, user_question)
    llm_response = await llm_client.chat.completions.create(..., messages=prompt)
    code_to_execute = extract_code_from_response(llm_response)

    # 2. Baixar o arquivo do Supabase e executar o código
    file_content = await supabase_storage.download(chat_context["original_file_path"])
    df = pd.read_csv(StringIO(file_content.decode()))
    
    execution_result = execute_sandboxed_code(df, code_to_execute) # FUNÇÃO CRÍTICA DE SEGURANÇA

    # 3. Chamar a LLM para sintetizar a resposta final
    final_prompt = build_synthesis_prompt(execution_result, user_question)
    final_response_stream = await llm_client.chat.completions.create(..., messages=final_prompt, stream=True)

    # 4. Enviar resposta via WebSocket em streaming
    full_response = ""
    async for chunk in final_response_stream:
        token = chunk.choices[0].delta.content or ""
        full_response += token
        await websocket_manager.send(chat_context["user_id"], {"token": token})

    # 5. Salvar a conversa no banco de dados
    await db.append_to_chat_history(chat_context["id"], user_question, full_response)


# Definição das tarefas do worker
class WorkerSettings:
    functions = [process_follow_up_question]
```

## 4\. Considerações e Riscos

  * **Segurança na Execução de Código:** Este é o **maior risco**. Executar código gerado por uma IA é perigoso. A função `execute_sandboxed_code` **NÃO** deve ser um simples `exec()`. É mandatório usar uma biblioteca de sandboxing (como `RestrictedPython`) ou, idealmente, executar o código em um container Docker efêmero e sem acesso à rede ou ao sistema de arquivos, para mitigar o risco de execução de código malicioso.
  * **Latência:** O download de arquivos grandes a cada pergunta pode gerar latência. Para o MVP, isso é aceitável. Pós-MVP, podemos implementar um cache (ex: Redis) que armazena o DataFrame em memória por alguns minutos após a primeira pergunta de acompanhamento.
  * **Precisão do LLM:** A LLM pode gerar código incorreto ou que quebra. O worker deve ter um bloco `try...except` robusto em torno da execução do código. Se falhar, ele deve notificar o usuário de forma amigável, como: `"Desculpe, não consegui realizar essa análise. Você poderia tentar reformular a sua pergunta?"`.

-----