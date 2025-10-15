

````markdown
# Documentação do Schema do Banco de Dados - MarData

## 1. Visão Geral e Arquitetura

O banco de dados do MarData é construído sobre **PostgreSQL** e hospedado no **Supabase**. A arquitetura foi projetada com dois princípios fundamentais em mente:

1.  **Segurança em Primeiro Lugar:** A privacidade dos dados do usuário é garantida em nível de banco de dados através do **Row Level Security (RLS)**. Nenhuma consulta, seja maliciosa ou acidental, pode acessar dados de outro usuário.
2.  **Integração Nativa:** O schema é totalmente integrado com os serviços do Supabase, especialmente o **Supabase Auth**. Isso simplifica a lógica de negócio no backend, delegando a gestão de usuários e as regras de acesso diretamente ao banco de dados.

## 2. Diagrama de Entidade-Relacionamento (ERD)

Este diagrama representa a relação entre as principais tabelas do sistema.

```mermaid
erDiagram
    "auth.users" ||--o{ "public.users" : "sincroniza"
    "public.users" ||--|{ notebooks : "possui"
    "public.users" ||--|{ files : "possui"
    notebooks ||--|{ messages : "contém"
    notebooks ||--|{ files : "contém"
````

  * **`auth.users` 1--1 `public.users`**: Cada usuário no sistema de autenticação do Supabase tem um perfil correspondente na tabela `users`.
  * **`users` 1--N `notebooks`**: Um usuário pode ter vários notebooks.
  * **`notebooks` 1--N `messages`**: Um notebook pode conter várias mensagens.
  * **`notebooks` 1--N `files`**: Um notebook pode estar associado a vários arquivos.

## 3\. Detalhamento das Tabelas

### Tabela `public.users`

Armazena informações públicas e de assinatura do usuário. Sincronizada com `auth.users`.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `UUID` (PK) | Chave primária. **Referencia `auth.users(id)`**. Garante a integridade. |
| `email` | `TEXT` (Unique) | E-mail do usuário, para referência. |
| `full_name`| `TEXT` | Nome completo do usuário. |
| `current_plan` | `plan` (Enum) | Plano de assinatura atual (`free`, `plus`, `premium`). Padrão: `free`. |
| `stripe_customer_id` | `TEXT` (Unique) | ID do cliente no Stripe para gestão de pagamentos. |
| `created_at`| `TIMESTAMPTZ` | Data de criação do perfil. |
| `updated_at`| `TIMESTAMPTZ` | Data da última atualização. |

### Tabela `public.notebooks`

Representa uma sessão de análise ou um chat individual.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `UUID` (PK) | Chave primária do notebook. |
| `user_id` | `UUID` (FK) | **Referencia `users(id)`**. O dono do notebook. |
| `title` | `TEXT` | Título do notebook, definido pelo usuário ou gerado automaticamente. |
| `analysis_cache` | `JSONB` | Cache do resultado da análise inicial (saída de `generate_descriptive_analysis`). Otimiza o desempenho do chat. |
| `created_at`| `TIMESTAMPTZ` | Data de criação. |
| `updated_at`| `TIMESTAMPTZ` | Data da última atualização. |

### Tabela `public.files`

Armazena os metadados dos arquivos enviados pelo usuário. O arquivo binário fica no Supabase Storage.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `UUID` (PK) | Chave primária do arquivo. |
| `notebook_id`| `UUID` (FK) | **Referencia `notebooks(id)`**. O notebook onde o arquivo foi usado. |
| `user_id` | `UUID` (FK) | **Referencia `users(id)`**. O usuário que fez o upload. |
| `storage_path`| `TEXT` (Unique) | Caminho completo para o objeto no Supabase Storage. |
| `file_name` | `TEXT` | Nome original do arquivo. |
| `file_type` | `TEXT` | MIME type do arquivo (ex: `text/csv`). |
| `file_size_bytes` | `BIGINT` | Tamanho do arquivo em bytes. |
| `created_at`| `TIMESTAMPTZ` | Data do upload. |

### Tabela `public.messages`

Armazena o histórico de mensagens de cada notebook.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `BIGINT` (PK) | Chave primária da mensagem. |
| `notebook_id`| `UUID` (FK) | **Referencia `notebooks(id)`**. A conversa à qual a mensagem pertence. |
| `role` | `message_role` (Enum) | O autor da mensagem (`user` ou `assistant`). |
| `content` | `TEXT` | O conteúdo textual da mensagem. |
| `created_at`| `TIMESTAMPTZ` | Data de envio da mensagem. |

## 4\. Tipos de Dados Customizados (Enums)

  * **`plan`**: Define os níveis de assinatura permitidos.
      * Valores: `'free'`, `'plus'`, `'premium'`.
  * **`message_role`**: Define quem é o autor de uma mensagem no chat.
      * Valores: `'user'`, `'assistant'`.

## 5\. Segurança e Automação

### Row Level Security (RLS)

O RLS está **ATIVADO** em todas as tabelas acima. As políticas garantem que:

  * **`users`**: Um usuário só pode ler e atualizar seu próprio registro de perfil.
  * **`notebooks` e `files`**: Um usuário só pode criar, ler, atualizar e deletar os notebooks e arquivos que ele mesmo criou (`user_id = auth.uid()`).
  * **`messages`**: Um usuário só pode ler e criar mensagens dentro dos notebooks que lhe pertencem. A verificação é feita por subconsulta, garantindo que o `notebook_id` da mensagem pertença a um notebook do usuário autenticado.

### Automação com Triggers

  * **Função `handle_new_user()` e Gatilho `on_auth_user_created`**:
      * **O que faz?** Automaticamente insere uma nova linha na tabela `public.users` sempre que um novo usuário se cadastra via Supabase Auth.
      * **Quando dispara?** `AFTER INSERT ON auth.users`.
      * **Propósito:** Garante a sincronização perfeita entre o sistema de autenticação e a tabela de perfis, simplificando a lógica da aplicação.

<!-- end list -->

```
```