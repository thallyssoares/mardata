2. Fluxo de Vida do Chat e Gerenciamento de Estado

O conceito de "sessão" é primariamente gerenciado pelo estado do cliente (Vue.js), com o backend validando e recuperando o estado persistido quando necessário.

a. Iniciação do Chat e Processamento Inicial (Cold Start)

    Upload: O usuário (autenticado via Supabase Auth) inicia um novo chat e faz o upload de um arquivo de dados.

    Armazenamento: O cliente Vue.js carrega o arquivo diretamente para o Supabase Storage em um bucket privado, associado ao user_id.

    Endpoint de Análise (POST /chat/initiate):

        O cliente invoca este endpoint no FastAPI, enviando a referência (path) do arquivo no Supabase Storage.

        O backend (FastAPI) utiliza suas credenciais de serviço para baixar o arquivo do Supabase Storage.

        Análise Estatística: O backend executa um processo de análise inicial no arquivo (ex: usando Pandas). Este processo gera um "Resumo Estatístico" (ex: um objeto JSON contendo df.info(), df.describe(), nomes de colunas, tipos de dados, contagem de valores nulos, etc.).

        Persistência: O backend armazena no Supabase (PostgreSQL):

            Metadados do chat (ID do chat, user_id, timestamp).

            A referência ao arquivo no Supabase Storage.

            O "Resumo Estatístico" gerado (ex: em uma coluna jsonb).

        Resposta: O backend retorna o ID do chat, o histórico (inicialmente vazio) e o Resumo Estatístico para o cliente Vue.js.

b. Gerenciamento da Sessão Ativa (Warm State)

    Estado do Cliente: O cliente Vue.js armazena em seu estado local (ex: Pinia) o Resumo Estatístico, a referência do arquivo e o histórico da conversa. Esta é a "sessão ativa".

    Endpoint de Mensagem (POST /chat/{chat_id}/message):

        Quando o usuário envia uma nova mensagem, o cliente Vue.js envia todo o contexto relevante para o backend:

            Nova mensagem do usuário.

            Histórico da conversa (ou últimas N mensagens).

            O "Resumo Estatístico" (cacheado no cliente).

        Contexto da IA: O backend formata este contexto (query, histórico, resumo) e o envia para o modelo de IA.

        Este fluxo evita que o backend precise consultar o banco de dados para obter o resumo a cada mensagem, otimizando a latência durante uma conversa contínua.

c. Resumo da Sessão (Re-hidratação do Estado)

    Fechamento: Quando o usuário fecha a aba, o estado do cliente Vue.js é perdido (a "sessão" se encerra). Nenhum evento de backend é necessário, pois o estado crítico já está persistido.

    Endpoint de Recuperação (GET /chat/{chat_id}):

        Quando o usuário reabre um chat existente, o cliente Vue.js (após autenticação) chama este endpoint.

        Validação: O backend utiliza o user_id (do token Supabase) e as políticas RLS do PostgreSQL para validar se o usuário tem permissão de acesso ao chat_id solicitado.

        Recuperação de Dados: O backend consulta o Supabase (PostgreSQL) e recupera o histórico de mensagens, a referência do arquivo e o "Resumo Estatístico" persistido.

        Re-hidratação: O backend retorna esses dados. O cliente Vue.js repopula seu estado local, restaurando efetivamente a "sessão ativa" para o estado de "Warm State" (item b).

3. Execução de Código Dinâmico (Pandas)

Este é o fluxo central quando a IA precisa de informações além do resumo estatístico.

    Decisão da IA: Durante o "Warm State" (passo 2b), a IA analisa a consulta do usuário e o Resumo Estatístico. A IA pode determinar que precisa executar código (ex: Pandas) no arquivo original para responder (ex: "quantos usuários têm mais de 30 anos?").

    Geração de Código: A IA, em vez de uma resposta em linguagem natural, retorna um bloco de código Python (ex: df[df['idade'] > 30].count()).

    Interceptação e Sanitização:

        O backend FastAPI intercepta esta resposta de código.

        O backend aplica uma camada de sanitização no código gerado para mitigar riscos óbvios (ex: remoção de imports de os, subprocess, operações de I/O de rede).

    Execução em Sandbox (POST /execute_code):

        O backend passa o código sanitizado para um ambiente de execução isolado (sandbox).

        Este ambiente (ex: um container Docker efêmero, firejail, ou um processo com seccomp) é pré-carregado com as bibliotecas necessárias (ex: Pandas, NumPy).

        O ambiente de sandbox recebe (ou baixa do Supabase Storage) o arquivo original do usuário em modo read-only.

        O código é executado dentro deste ambiente restrito, carregando o arquivo em um dataframe (ex: df = pd.read_csv(...)) e executando a lógica gerada pela IA.

    Captura de Saída: O stdout ou o valor de retorno da execução (ex: o resultado de .count()) é capturado pelo backend.

    Ciclo de Feedback da IA:

        O backend envia o resultado da execução de volta para a IA, juntamente com a consulta original.

        A IA utiliza este novo dado (ex: "57") para formular a resposta final em linguagem natural (ex: "Existem 57 usuários com mais de 30 anos.").

    Resposta Final: O backend envia esta resposta final em linguagem natural para o cliente Vue.js.

4. Vantagens da Arquitetura

    Eficiência: A análise pesada do arquivo (geração do resumo) é feita apenas uma vez.

    Otimização de Latência: Durante a "sessão ativa", o resumo estatístico é cacheado no cliente, reduzindo consultas ao DB a cada turno da conversa.

    Flexibilidade: A IA não se limita ao resumo; ela pode executar código on-demand no arquivo original para consultas complexas.

    Segurança: A execução de código gerado por IA é contida em um ambiente sandboxed, protegendo a infraestrutura do backend contra execuções de código arbitrárias.

    Persistência: O estado do chat (incluindo o resumo) é persistido no Supabase, permitindo que o usuário retome a análise de onde parou.