# Documento de Endpoints da API - Sessão Certa

## Introdução

Este documento descreve os endpoints da API RESTful para o produto Sessão Certa, um SaaS de gerenciamento de agendamentos para pequenos comerciantes (ex.: barbeiros, salões de beleza, etc). A API é projetada para suportar as funcionalidades descritas nos requisitos funcionais (RF001 a RF025) e casos de uso (UC001 a UC015), incluindo autenticação, gerenciamento de agendamentos, funcionários, clientes finais, estoque, relatórios contábeis, ~~mensagens customizáveis~~ e integrações externas (ex.: WhatsApp, pagamentos).

A API segue o padrão REST, utiliza JSON para requisições e respostas, e é implementada com FastAPI (Python). Autenticação é baseada em JWT, com roles: `admin` (administrador), `client` (cliente/dono do estabelecimento) e `employee` (funcionário). Endpoints sensíveis requerem autorização.

- **Base URL**: `/api/v1`
- **Autenticação**: Token JWT no header `Authorization: Bearer <token>`
- **Erros comuns**: 
  - 400: Requisição inválida
  - 401: Não autorizado
  - 403: Acesso proibido
  - 404: Não encontrado
  - 500: Erro interno
- **Paginação**: Para listas, use query params `page` (página, default 1) e `limit` (itens por página, default 10)
- **Filtros**: Suporte a query params para filtros (ex.: `date_start`, `date_end`)

## Autenticação e Registro

| Método | Caminho | Descrição | Parâmetros de Query | Corpo da Requisição | Resposta |
|--------|---------|-----------|---------------------|---------------------|----------|
| POST | /auth/register | Registra um novo cliente após compra de plano (RF002, RF014, RF025, UC002). Integra com gateway de pagamento. Coleta dados do cliente e do estabelecimento em um corpo aninhado, refletindo as entidades separadas no modelo de dados (Client e Establishment, com relação 1:1). | `plan_id` (ID do plano, obrigatório) | `{ "client": { "name": "string", "email": "string", "password": "string", "phone": "string" }, "establishment": { "name": "string", "address": "string", "cnpj": "string", "trialActive": bool } }` | 201: `{ "user_id": "uuid", "token": "string" }` <br> 400: Erro de validação <br> 402: Pagamento falhou |
| POST | /auth/login | Autentica usuário (cliente, funcionário ou admin) (RF022, UC014). | - | `{ "email": "string", "password": "string" }` | 200: `{ "token": "string", "role": "string" }` <br> 401: Credenciais inválidas |
| POST | /auth/recover-password | Inicia recuperação de senha via e-mail (RF022, UC014). | - | `{ "email": "string" }` | 200: `{ "message": "Código enviado" }` <br> 404: E-mail não encontrado |
| POST | /auth/reset-password | Reseta senha com código de verificação (RF022, UC014). | `code` (código de verificação, obrigatório) | `{ "new_password": "string" }` | 200: `{ "message": "Senha atualizada" }` <br> 400: Código inválido |

## Planos e Assinaturas

| Método | Caminho | Descrição | Parâmetros de Query | Corpo da Requisição | Resposta |
|--------|---------|-----------|---------------------|---------------------|----------|
| GET | /plans | Lista planos disponíveis (Bronze, Prata, Ouro) (RF019, RF025, UC015). | - | - | 200: `[{ "id": "uuid", "name": "string", "price": "decimal", "features": ["array"] }]` |
| GET | /plans/my-plan | Obtém detalhes do plano atual do cliente (RF019, UC015). Requer role `client`. | - | - | 200: `{ "id": "uuid", "name": "string", "employees_limit": "int", ... }` |
| PUT | /plans/upgrade | Atualiza ou altera plano, processando pagamento recorrente (RF019, RF020, UC015). Requer role `client`. | `plan_id` (novo plano, obrigatório) | - | 200: `{ "message": "Plano atualizado" }` <br> 402: Pagamento falhou |
| POST | /plans/cancel | Cancela assinatura (RF019, UC015). Requer role `client`. | - | - | 200: `{ "message": "Assinatura cancelada" }` |

## Estabelecimentos

| Método | Caminho | Descrição | Parâmetros de Query | Corpo da Requisição | Resposta |
|--------|---------|-----------|---------------------|---------------------|----------|
| GET | /establishments | Obtém dados do estabelecimento do cliente (RF002). Requer role `client`. | - | - | 200: `{ "id": "uuid", "name": "string", "address": "string", ... }` |
| PUT | /establishments | Atualiza dados do estabelecimento (RF002). Requer role `client`. | - | `{ "name": "string", "address": "string", "atributos": [array] }` | 200: `{ "message": "Atualizado" }` |

## Funcionários (Employees)

| Método | Caminho | Descrição | Parâmetros de Query | Corpo da Requisição | Resposta |
|--------|---------|-----------|---------------------|---------------------|----------|
| GET | /employees | Lista funcionários do estabelecimento (RF005, RF024, UC005). Requer role `client`. | `search` (filtro por nome), `page`, `limit` | - | 200: `[{ "id": "uuid", "name": "string", "commission": "decimal", "appointments_count": "int" }]` |
| GET | /employees/{id} | Obtém detalhes de um funcionário (RF005). Requer role `client`. | - | - | 200: `{ "id": "uuid", "name": "string", ... }` |
| POST | /employees | Adiciona novo funcionário, criando conta herdeira (RF005, RF024, UC005). Limite por plano. Requer role `client`. | - | `{ "name": "string", "email": "string", "password": "string", "commission": "decimal", "permissions": ["array"] }` | 201: `{ "id": "uuid" }` <br> 403: Limite de funcionários atingido |
| PUT | /employees/{id} | Atualiza funcionário (comissões, permissões, horários) (RF005, RF024). Requer role `client`. | - | `{ "commission": "decimal", "permissions": ["array"] }` | 200: `{ "message": "Atualizado" }` |
| DELETE | /employees/{id} | Remove funcionário, realocando agendamentos (RF005). Requer role `client`. | - | - | 204: No content |

## Serviços (Services)

| Método | Caminho | Descrição | Parâmetros de Query | Corpo da Requisição | Resposta |
|--------|---------|-----------|---------------------|---------------------|----------|
| GET | /services | Lista serviços oferecidos (RF015). Requer role `client` ou `employee`. | `page`, `limit` | - | 200: `[{ "id": "uuid", "name": "string", "price": "decimal", "duration": "int" }]` |
| POST | /services | Adiciona novo serviço (RF015). Requer role `client`. | - | `{ "name": "string", "price": "decimal", "duration": "int" }` | 201: `{ "id": "uuid" }` |
| PUT | /services/{id} | Atualiza serviço (RF015). Requer role `client`. | - | `{ "price": "decimal" }` | 200: `{ "message": "Atualizado" }` |
| DELETE | /services/{id} | Remove serviço (RF015). Requer role `client`. | - | - | 204: No content |

## Agendamentos (Scheduling)

| Método | Caminho | Descrição | Parâmetros de Query | Corpo da Requisição | Resposta |
|--------|---------|-----------|---------------------|---------------------|----------|
| GET | /appointments | Lista agendamentos (calendário, filtros) (RF004, RF017, RF018, UC004). Requer role `client` ou `employee` (próprios). | `date_start`, `date_end`, `employee_id`, `status`, `page`, `limit` | - | 200: `[{ "id": "uuid", "date": "datetime", "customer_name": "string", "service_name": "string", "status": "enum" }]` |
| GET | /appointments/{id} | Obtém detalhes de agendamento (RF004). Requer role `client` ou `employee`. | - | - | 200: `{ "id": "uuid", ... }` |
| POST | /appointments | Cria agendamento manual (RF004, RF003 via internal). Verifica conflitos. Requer role `client` ou `employee`. | - | `{ "customer_id": "uuid", "service_id": "uuid", "employee_id": "uuid", "date": "datetime" }` | 201: `{ "id": "uuid" }` <br> 409: Conflito de horário |
| PUT | /appointments/{id} | Atualiza agendamento (RF004). Requer role `client` ou `employee`. | - | `{ "date": "datetime" }` | 200: `{ "message": "Atualizado" }` |
| DELETE | /appointments/{id} | Cancela agendamento, envia notificação (RF004, RF010). Requer role `client` ou `employee`. | - | - | 204: No content |
| GET | /appointments/export | Exporta agendamentos (CSV/PDF) (RF016). Requer role `client`. | `format` (csv/pdf), `date_start`, `date_end` | - | 200: Arquivo binário |

## Clientes Finais (Costumers)

| Método | Caminho | Descrição | Parâmetros de Query | Corpo da Requisição | Resposta |
|--------|---------|-----------|---------------------|---------------------|----------|
| GET | /customers | Lista clientes finais com análises (histórico, preferências) (RF006, UC006). Requer role `client`. | `search` (nome/telefone), `page`, `limit` | - | 200: `[{ "id": "uuid", "name": "string", "appointments_count": "int"]` |
| GET | /customers/{id} | Obtém detalhes de cliente final (RF006). Requer role `client`. | - | - | 200: `{ "id": "uuid", ... }` |

## Estoque (Stock - Plano Ouro)

| Método | Caminho | Descrição | Parâmetros de Query | Corpo da Requisição | Resposta |
|--------|---------|-----------|---------------------|---------------------|----------|
| GET | /stock/products | Lista produtos em estoque (RF007, UC007). Requer role `client` e plano Ouro. | `page`, `limit` | - | 200: `[{ "id": "uuid", "name": "string", "quantity": "int", "price": "decimal" }]` |
| POST | /stock/products | Adiciona produto (RF007). Requer role `client` e plano Ouro. | - | `{ "name": "string", "quantity": "int", "price": "decimal" }` | 201: `{ "id": "uuid" }` |
| PUT | /stock/products/{id} | Atualiza produto (RF007). Requer role `client` e plano Ouro. | - | `{ "quantity": "int" }` | 200: `{ "message": "Atualizado" }` |
| DELETE | /stock/products/{id} | Remove produto (RF007). Requer role `client` e plano Ouro. | - | - | 204: No content |
| POST | /stock/movements | Registra movimento de estoque (entrada/saída/ajuste) (RF007). Requer role `client` e plano Ouro. | - | `{ "product_id": "uuid", "type": "enum", "quantity": "int" }` | 201: `{ "id": "uuid" }` |

## Relatórios Contábeis

| Método | Caminho | Descrição | Parâmetros de Query | Corpo da Requisição | Resposta |
|--------|---------|-----------|---------------------|---------------------|----------|
| GET | /reports/financial | Gera relatório financeiro (rendimentos por período, atendimentos) (RF008, RF016, UC008). Requer role `client`. | `period` (daily/weekly/monthly/annual), `start_date`, `end_date` | - | 200: `{ "total_revenue": "decimal", "appointments_count": "int", "details": "json" }` |
| GET | /reports/export | Exporta relatório (CSV/PDF) (RF016). Requer role `client`. | `format` (csv/pdf), `period` | - | 200: Arquivo binário |

## ~~Mensagens Customizáveis (Marketing - Planos Prata/Ouro)~~

| ~~Método~~ | ~~Caminho~~ | ~~Descrição~~ | ~~Parâmetros de Query~~ | ~~Corpo da Requisição~~ | ~~Resposta~~ |
|------------|-------------|---------------|---------------------------|---------------------------|--------------|
| ~~POST~~ | ~~\/marketing\/messages~~ | ~~Cria e envia mensagem customizável via WhatsApp (RF009, RF021, UC009). Requer role `client` e plano Prata/Ouro.~~ | ~~`segment` (filtro de usuários)~~ | ~~`{ "content": "string" }`~~ | ~~201: `{ "id": "uuid", "sent_count": "int" }` <br> 403: Plano não permite~~ |


## Notificações

| Método | Caminho | Descrição | Parâmetros de Query | Corpo da Requisição | Resposta |
|--------|---------|-----------|---------------------|---------------------|----------|
| POST | /notifications/reminders | Envia lembrete manual para agendamento (RF010, UC010). Requer role `client` ou `employee`. | `appointment_id` (obrigatório) | - | 200: `{ "message": "Lembrete enviado" }` |

## Integrações Externas (Internal/Admin)

| Método | Caminho | Descrição | Parâmetros de Query | Corpo da Requisição | Resposta |
|--------|---------|-----------|---------------------|---------------------|----------|
| POST | /integrations/whatsapp/webhook | Webhook para chatbot WhatsApp (RF003, RF012, UC003). Internal. | - | Payload do WhatsApp | 200: Confirmação |
| POST | /integrations/payment/webhook | Webhook para gateway de pagamento (RF014). Internal. | - | Payload do gateway | 200: Confirmação |

## Administração (Admin Only)

| Método | Caminho | Descrição | Parâmetros de Query | Corpo da Requisição | Resposta |
|--------|---------|-----------|---------------------|---------------------|----------|
| GET | /admin/clients | Lista todos clientes (RF013, RF023, UC013). Requer role `admin`. | `page`, `limit` | - | 200: `[{ "id": "uuid", "name": "string", "plan": "string", "usage_metrics": "json" }]` |
| GET | /admin/metrics | Obtém métricas globais (churn, uso) (RF013, RF023). Requer role `admin`. | - | - | 200: `{ "total_clients": "int", "churn_rate": "decimal", ... }` |
| PUT | /admin/clients/{id} | Atualiza conta de cliente (RF013). Requer role `admin`. | - | `{ "plan_id": "uuid" }` | 200: `{ "message": "Atualizado" }` |