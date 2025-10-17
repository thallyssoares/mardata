Entendido. Foco total em performance.

Você está certo em se concentrar nisso, pois a *percepção* de velocidade é tão importante quanto a velocidade real do processamento. Uma interface que "conversa" com o usuário durante a espera parece muito mais rápida do que uma que simplesmente exibe um spinner.

Aqui está o PRD reestruturado para focar exclusivamente nas funcionalidades que garantem a velocidade e a fluidez do sistema, com prompts específicos para a IA de desenvolvimento.

-----

## **PRD de Performance: Otimização do MarData**

**Versão:** 1.1
**Foco:** Garantir que a plataforma seja e se sinta excepcionalmente rápida, mesmo com grandes volumes de dados e tarefas complexas de IA.

### 1\. Visão Geral

O sucesso do MarData depende de uma experiência de usuário fluida e interativa. A análise de dados pode ser demorada, mas o usuário jamais deve se sentir bloqueado ou incerto sobre o progresso. Este documento detalha os requisitos funcionais e técnicos para construir um sistema de alta performance, focando no processamento de dados, na interatividade do chat e na otimização da camada de IA.

### 2\. Objetivos e Métricas de Sucesso

| Objetivo Estratégico | Métrica Chave de Performance (KPI) | Meta para o MVP |
| :--- | :--- | :--- |
| **Eliminar o gargalo de memória** | Consumo de RAM no worker durante o processamento | \< 1GB para um arquivo de 500MB |
| **Garantir interatividade instantânea** | Time-to-First-Token (TTFT) no chat | \< 3 segundos |
| **Tornar a espera "produtiva"** | Nº de status de progresso enviados por análise | Mínimo de 3 status distintos |
| **Acelerar análises recorrentes** | Redução no tempo de leitura do arquivo após 1ª análise | \> 70% |

### 3\. Requisitos Funcionais e Prompts de Geração de Código

-----

#### **ÉPICO 1: Processamento de Dados de Alta Performance**

> *Como sistema, quero processar planilhas grandes de forma eficiente para evitar travamentos e entregar a primeira análise o mais rápido possível, preparando o terreno para futuras interações velozes.*

-----

**História de Usuário 1.1: Processamento de Arquivos em Blocos (Chunking)**

  * **Descrição:** O worker do backend deve ser capaz de processar planilhas que são maiores que a memória RAM disponível, lendo e analisando o arquivo em pedaços sequenciais.

  * **PROMPT PARA IA (BACKEND - PYTHON/PANDAS):**

    ```prompt
    Atue como um Engenheiro de Dados Sênior. Refatore a função de processamento de planilhas em um worker Python (RQ/Celery) para garantir baixo consumo de memória ao lidar com arquivos grandes.

    **Tarefa:** Crie a função `process_spreadsheet_in_chunks(file_path: str) -> dict`.

    **Requisitos:**
    1.  **Leitura Eficiente:** Utilize a biblioteca Pandas. Ao ler o arquivo CSV (`file_path`), use o parâmetro `chunksize=50000` para criar um iterador.
    2.  **Agregação de Sumário:** Itere sobre cada `chunk`. Para cada um, calcule estatísticas descritivas parciais. Ao final, consolide esses resultados parciais em um único dicionário de sumário final (contendo médias, desvios padrão, contagens, etc., para as colunas numéricas).
    3.  **Memória:** A lógica deve ser projetada para que em nenhum momento o arquivo inteiro seja carregado na memória. O consumo de RAM deve permanecer baixo e estável.
    4.  **Retorno:** A função deve retornar o dicionário com o sumário estatístico consolidado.
    5.  **Padrões:** Use type hinting, siga a PEP 8 e escreva docstrings claras no estilo Google.
    ```

-----

**História de Usuário 1.2: Conversão para Formato Otimizado (Parquet)**

  * **Descrição:** Após a primeira análise de um arquivo, o sistema deve convertê-lo para o formato Parquet e salvá-lo, para que todas as futuras consultas do chat no mesmo notebook sejam ordens de magnitude mais rápidas.

  * **PROMPT PARA IA (BACKEND - PYTHON/PANDAS):**

    ```prompt
    Atue como um Engenheiro de Backend. Crie uma função assíncrona para ser executada após a primeira análise de uma planilha. A função deve converter o arquivo original para o formato Parquet para otimizar leituras futuras.

    **Tarefa:** Crie a função `convert_to_parquet_and_update_record(original_file_path: str, notebook_id: int)`.

    **Requisitos:**
    1.  **Leitura e Conversão:**
        * Leia o arquivo original (CSV ou Excel) do `original_file_path` usando Pandas (pode ser em chunks se for muito grande).
        * Crie um novo caminho de arquivo, trocando a extensão para `.parquet`.
        * Use a função `dataframe.to_parquet()` para salvar o dataframe no novo formato.
    2.  **Armazenamento:** Faça o upload do novo arquivo `.parquet` para o Supabase Storage.
    3.  **Atualização do Banco de Dados:**
        * Conecte-se ao banco de dados do Supabase.
        * Atualize a tabela `notebooks` na linha correspondente ao `notebook_id`.
        * Modifique um campo (ex: `optimized_file_path`) para apontar para o caminho do novo arquivo Parquet.
    4.  **Limpeza:** Delete o arquivo Parquet local após o upload bem-sucedido.
    ```

-----

#### **ÉPICO 2: Experiência de Chat Instantânea e Transparente**

> *Como usuário, quero que a interface responda imediatamente às minhas perguntas, mostrando o progresso do "raciocínio" da IA e entregando a resposta de forma contínua, para que a interação seja natural e fluida.*

-----

**História de Usuário 2.1: Streaming de Respostas Token-por-Token**

  * **Descrição:** A resposta final do Agente de Síntese não deve ser enviada de uma só vez. Ela deve ser transmitida (streamed) para o frontend token por token assim que é gerada.

  * **PROMPT PARA IA (BACKEND - FASTAPI):**

    ```prompt
    Atue como um Especialista em FastAPI. Modifique o endpoint de WebSocket (`/ws/notebook/{notebook_id}`) para suportar o streaming de respostas de um LLM.

    **Contexto:** O fluxo de orquestração dos agentes de IA culmina na chamada a um `SynthesisAgent`, que possui um método `stream_response()`. Este método é um gerador (`yields tokens`).

    **Tarefa:** Implemente a lógica dentro do endpoint WebSocket.

    **Requisitos:**
    1.  **Chamada em Stream:** Invoque o agente de síntese no modo de streaming. Ex: `response_generator = SynthesisAgent.stream_response(data)`.
    2.  **Transmissão de Tokens:** Itere sobre o gerador. A cada token recebido, envie imediatamente uma mensagem JSON para o cliente WebSocket conectado.
    3.  **Formato da Mensagem:** A mensagem deve ser estruturada para fácil parseamento no frontend. Formato: `{"status": "streaming", "token": "o token recebido"}`.
    4.  **Mensagem de Conclusão:** Após o término do loop, envie uma mensagem final para sinalizar o fim da transmissão. Formato: `{"status": "done"}`.
    ```

  * **PROMPT PARA IA (FRONTEND - VUE.JS/PINIA):**

    ```prompt
    Atue como um Desenvolvedor Vue.js Sênior. Implemente a lógica no frontend para receber e renderizar uma resposta de texto via streaming por WebSocket.

    **Contexto:** O componente de chat (`Chat.vue`) tem uma conexão WebSocket ativa e um listener `socket.onmessage`. O estado do chat é gerenciado por uma store Pinia (`useChatStore`), que contém um array `messages`.

    **Tarefa:** Escreva a lógica dentro do `socket.onmessage` handler.

    **Requisitos:**
    1.  **Parseamento:** Parseie a mensagem JSON recebida do WebSocket.
    2.  **Lógica de Renderização:**
        * **Primeiro Token:** Se `data.status === 'streaming'` e for o primeiro token da resposta, adicione um novo objeto de mensagem ao array `messages` em Pinia (ex: `{ id: ..., role: 'ai', content: data.token }`).
        * **Tokens Subsequentes:** Se `data.status === 'streaming'` e não for o primeiro, encontre a última mensagem da IA no array e anexe o `data.token` ao seu campo `content`.
    3.  **Reatividade:** A interface deve ser reativa. Conforme a propriedade `content` da mensagem é atualizada na store, a UI deve renderizar o texto progressivamente, criando o efeito de digitação.
    ```

-----

**História de Usuário 2.2: Indicadores de Progresso Granulares**

  * **Descrição:** Enquanto o backend processa uma solicitação, ele deve enviar múltiplas mensagens de status para o frontend, informando ao usuário exatamente em que etapa do processo a IA está.

  * **PROMPT PARA IA (BACKEND - PYTHON/FASTAPI):**

    ```prompt
    Atue como um Arquiteto de Software. Instrumente a função do Agente Orquestrador para que ela envie atualizações de status via WebSockets em pontos-chave do seu processo de decisão.

    **Contexto:** O Agente Orquestrador executa um plano de ação, delegando tarefas para outros agentes (Análise de Dados, Contexto de Mercado, etc.). Ele tem acesso ao objeto de conexão WebSocket do usuário atual.

    **Tarefa:** Adicione chamadas `websocket.send_json()` dentro da lógica do orquestrador.

    **Exemplos de Implementação:**
    1.  **Antes de chamar o Agente de Análise:**
        `await websocket.send_json({"status": "processing", "message": "Entendi. Estou validando uma hipótese nos seus dados..."})`
    2.  **Antes de chamar o Agente de Contexto (RAG):**
        `await websocket.send_json({"status": "processing", "message": "Os números parecem indicar algo. Estou consultando benchmarks de mercado para dar contexto..."})`
    3.  **Antes de chamar o Agente de Síntese:**
        `await websocket.send_json({"status": "processing", "message": "Ótimo. Compilando os insights em um relatório acionável..."})`

    O objetivo é que o código final tenha essas mensagens de "pensamento em voz alta" intercaladas com as chamadas de lógica principal.
    ```