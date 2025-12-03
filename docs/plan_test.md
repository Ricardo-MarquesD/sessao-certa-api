# Plano de Testes - Sessão Certa

## Introdução

Este plano de testes descreve a estratégia completa para validar o produto Sessão Certa, um SaaS de gerenciamento de agendamentos para pequenos comerciantes (ex.: barbeiros, salões de beleza). O plano é baseado nos requisitos funcionais (RF001 a RF025), não funcionais (RNF001 a RNF016), regras de negócio, casos de uso (UC001 a UC015), diagramas de sequência, classes e modelo de banco de dados do documento de análise de requisitos, bem como nos endpoints da API RESTful definidos no documento de endpoints (implementados em FastAPI com autenticação JWT e roles: admin, client, employee).

Como se trata de um produto real, o plano enfatiza cobertura abrangente, automação onde possível, conformidade com LGPD (segurança e privacidade de dados), escalabilidade e usabilidade. Os testes cobrem a API backend, integrações externas (WhatsApp, pagamentos), dashboard frontend (protótipos de interface) e chatbot. Ferramentas recomendadas incluem Pytest para unitários/integração, Postman/Newman para API, Selenium/Cypress para E2E/UI, JMeter para performance e OWASP ZAP para segurança.

## Objetivos

- Verificar que todos os requisitos funcionais e não funcionais são atendidos.
- Garantir a estabilidade, segurança e performance do sistema em cenários reais (ex.: múltiplos agendamentos simultâneos, limites de planos).
- Identificar defeitos precocemente para minimizar riscos em produção.
- Validar fluxos de usuários (clientes, funcionários, usuários finais, admins) conforme casos de uso.
- Assegurar conformidade com regras de negócio (ex.: limites de funcionários por plano) e restrições de software (navegadores modernos, MySQL, WhatsApp Business API).
- Cobertura mínima: 80% para testes unitários/integração (RNF016), 100% para casos críticos (agendamentos, pagamentos).

## Escopo

- **Em escopo**: Testes para todos os endpoints da API (/auth, /plans, /establishments, /employees, /services, /appointments, /customers, /stock, /reports, /marketing, /notifications, /integrations, /admin). Integrações com WhatsApp (chatbot), gateway de pagamentos e calendários externos. Fluxos E2E baseados em UC e RF. Testes não funcionais (performance, segurança, usabilidade).
- **Fora de escopo**: Testes de hardware, rede externa (além de simulações), conformidade legal além de LGPD básica, testes em produção inicial (foco em staging/dev).
- Ambientes: Desenvolvimento (local), Staging (nuvem simulada), Produção (após aprovação).

## Estratégia de Testes

### Níveis de Testes
1. **Testes Unitários** (Cobertura: Métodos individuais, validações):
   - Ferramenta: Pytest (Python).
   - Foco: Lógica de negócios (ex.: verificação de conflitos de horário em Scheduling), enums (typePlan, appointmentStatus), classes do modelo (UserAbstract, Establishment).
   - Execução: Automatizada via CI/CD (GitHub Actions/Jenkins).
   - Critério de aceitação: 80% cobertura (RNF016).

2. **Testes de Integração** (Cobertura: Interações entre componentes):
   - Ferramenta: Pytest com mocks (ex.: mockar Banco de Dados MySQL, APIs externas).
   - Foco: Endpoints com DB (ex.: POST /appointments verifica disponibilidade via query SQL), integrações (webhooks WhatsApp/Pagamentos), roles JWT (ex.: acesso negado para employee em /employees).
   - Execução: Automatizada, pós-unitários.

3. **Testes de Sistema/E2E** (Cobertura: Fluxos completos):
   - Ferramenta: Postman para API, Selenium para dashboard/protótipos UI.
   - Foco: Casos de uso end-to-end (ex.: UC003 - Agendar via ChatBot, sincronizar com dashboard). Testar diagramas de sequência (ex.: login -> credenciamento -> agendamento).
   - Execução: Manual/automatizada, em staging.

4. **Testes Não Funcionais**:
   - **Performance** (RNF002): JMeter para simular 500 usuários (RNF005), resposta <3s em consultas.
   - **Segurança** (RNF003): OWASP ZAP para vulnerabilidades (XSS, SQL Injection), testes de JWT (expiração, roles), criptografia de dados sensíveis (LGPD).
   - **Usabilidade** (RNF001, RNF010): Testes manuais em mobile/desktop, WCAG compliance.
   - **Disponibilidade** (RNF004): Testes de failover, uptime 98%.
   - **Escalabilidade** (RNF005): Cargas crescentes em nuvem.
   - **Compatibilidade** (RNF006): Testes em Chrome, Edge, mobile browsers.
   - **Outros**: Backup/recuperação (RNF014), logs/audit (RNF012), internacionalização (RNF011).

5. **Testes de Aceitação**:
   - Baseados em UC/RF, com usuários reais (beta testers: barbeiros).
   - Critério: Aprovação de stakeholders.

### Tipos de Testes
- **Positivos (Happy Path)**: Fluxos normais (ex.: registro válido).
- **Negativos**: Erros esperados (ex.: 401 sem token, 403 limite de plano excedido).
- **Edge Cases**: Limites (ex.: máximo funcionários por plano, agendamentos simultâneos).
- **Exploratórios**: Para usabilidade no protótipo UI.
- **Regressão**: Automatizados para endpoints críticos após mudanças.

### Ferramentas e Recursos
- Código: Python/FastAPI (backend), MySQL (DB).
- Testes API: Postman collections para cada módulo.
- Automação: Pytest, Selenium.
- Monitoramento: Logs (RNF015), tools como New Relic.
- Equipe: Desenvolvedores (unit/integração), QA (sistema), Usuários beta (aceitação).
- Dados de Teste: Ambientes com dados mockados (Faker lib), respeitando LGPD.

### Cronograma
- Fase 1 (Desenvolvimento): Unitários paralelos ao código (2 semanas).
- Fase 2 (Integração): Após features prontas (1 semana por módulo).
- Fase 3 (Sistema/Não Funcionais): Staging (3 semanas).
- Fase 4 (Aceitação): Beta (2 semanas).
- Total: 8 semanas, com regressão semanal.

### Riscos e Mitigações
- Risco: Integrações externas falharem (WhatsApp, pagamentos) - Mitigação: Mocks e testes simulados.
- Risco: Performance em picos - Mitigação: Load testing precoce.
- Risco: Segurança (vazamento dados) - Mitigação: Audits regulares.
- Risco: Cobertura incompleta - Mitigação: Mapeamento RF/UC para testes.

## Casos de Teste Detalhados

Organizados por módulo/endpoint, mapeados a RF/UC/RNF. Cada caso inclui: ID, Descrição, Pré-condições, Passos, Resultado Esperado, Critério de Aceitação.

### 1. Autenticação e Registro (/auth)
- Mapeamento: RF002, RF014, RF022, RF025, UC002, UC014, RNF003 (segurança JWT).

| ID | Descrição | Pré-condições | Passos | Resultado Esperado | Critério |
|----|-----------|----------------|--------|---------------------|----------|
| TC_AUTH_01 | Registro válido pós-compra (happy path) | Plano ID válido, gateway mock aprovado. | 1. POST /auth/register com dados client/establishment válidos. | 201, retorna user_id e token. Conta criada no DB com plano associado. | RF002, UC002. |
| TC_AUTH_02 | Registro com pagamento falhado | Gateway mock recusa. | 1. POST /auth/register. | 402 Pagamento falhou. | RF014. |
| TC_AUTH_03 | Login válido (client role) | Conta registrada. | 1. POST /auth/login com credenciais. | 200, token e role "client". | RF022, UC014. |
| TC_AUTH_04 | Login inválido | Credenciais erradas. | 1. POST /auth/login. | 401 Credenciais inválidas. | RF022. |
| TC_AUTH_05 | Recuperação de senha | E-mail cadastrado. | 1. POST /auth/recover-password. 2. POST /auth/reset-password com code válido. | 200 Código enviado/Senha atualizada. | RF022, UC014. |
| TC_AUTH_06 | Reset com code inválido | Code expirado. | 1. POST /auth/reset-password. | 400 Código inválido. | RF022. |
| TC_AUTH_07 | Segurança JWT | Token inválido/expirado. | 1. Chamar endpoint protegido sem/ com token inválido. | 401/403. | RNF003. |
| TC_AUTH_08 | Edge: Registro com dados duplicados (e-mail) | E-mail já usado. | 1. POST /auth/register. | 400 Erro de validação (duplicado). | RF002. |

### 2. Planos e Assinaturas (/plans)
- Mapeamento: RF019, RF020, RF025, UC015, RN01-04 (planos Bronze/Prata/Ouro).

| ID | Descrição | Pré-condições | Passos | Resultado Esperado | Critério |
|----|-----------|----------------|--------|---------------------|----------|
| TC_PLANS_01 | Listar planos disponíveis | Nenhum (público). | 1. GET /plans. | 200, lista com Bronze, Prata, Ouro e features. | RF019. |
| TC_PLANS_02 | Obter meu plano (client) | Logado como client. | 1. GET /plans/my-plan. | 200, detalhes do plano atual (ex.: employees_limit). | RF019, UC015. |
| TC_PLANS_03 | Upgrade de plano | Logado, gateway mock aprovado. | 1. PUT /plans/upgrade com plan_id. | 200 Plano atualizado. | RF019, RF020. |
| TC_PLANS_04 | Upgrade falhado (pagamento) | Gateway recusa. | 1. PUT /plans/upgrade. | 402 Pagamento falhou. | RF020. |
| TC_PLANS_05 | Cancelar assinatura | Logado como client. | 1. POST /plans/cancel. | 200 Assinatura cancelada. | RF019. |
| TC_PLANS_06 | Acesso negado (não client) | Logado como employee. | 1. GET /plans/my-plan. | 403 Acesso proibido. | RNF003. |
| TC_PLANS_07 | Edge: Upgrade para mesmo plano | Logado. | 1. PUT /plans/upgrade com mesmo plan_id. | 400 Requisição inválida. | RF019. |
| TC_PLANS_08 | Performance: Listar planos com 500 reqs/simultâneas | - | Simular carga. | Resposta <3s (RNF002). | RNF005. |

### 3. Estabelecimentos (/establishments)
- Mapeamento: RF002, UC002 (credenciamento).

| ID | Descrição | Pré-condições | Passos | Resultado Esperado | Critério |
|----|-----------|----------------|--------|---------------------|----------|
| TC_EST_01 | Obter dados estabelecimento | Logado como client. | 1. GET /establishments. | 200, dados (name, address). | RF002. |
| TC_EST_02 | Atualizar estabelecimento | Logado como client. | 1. PUT /establishments com dados. | 200 Atualizado. | RF002. |
| TC_EST_03 | Acesso como employee | Logado como employee. | 1. GET /establishments. | 200 (visualização ok). | RF002. |
| TC_EST_04 | Atualização negada (employee) | Logado como employee. | 1. PUT /establishments. | 403 Proibido. | RNF003. |
| TC_EST_05 | Edge: Dados inválidos | Logado. | 1. PUT com address vazio. | 400 Validação falha. | RF002. |

### 4. Funcionários (/employees)
- Mapeamento: RF005, RF024, UC005, limites por plano (RN).

| ID | Descrição | Pré-condições | Passos | Resultado Esperado | Critério |
|----|-----------|----------------|--------|---------------------|----------|
| TC_EMP_01 | Listar funcionários | Logado como client, plano Bronze (limite 1). | 1. GET /employees. | 200, lista. | RF005. |
| TC_EMP_02 | Adicionar funcionário | Logado, abaixo limite. | 1. POST /employees com dados. | 201, ID retornado. Conta herdeira criada. | RF005, UC005. |
| TC_EMP_03 | Adicionar além limite | Plano Bronze, já 1 employee. | 1. POST /employees. | 403 Limite atingido. | RF005, RN02. |
| TC_EMP_04 | Atualizar funcionário | Logado. | 1. PUT /employees/{id}. | 200 Atualizado. | RF024. |
| TC_EMP_05 | Remover funcionário | Logado. | 1. DELETE /employees/{id}. | 204, agendamentos realocados. | RF005. |
| TC_EMP_06 | Acesso negado (employee) | Logado como employee. | 1. GET /employees. | 403 Proibido. | RNF003. |
| TC_EMP_07 | Edge: Comissão negativa | Logado. | 1. POST com commission negativa. | 400 Inválido. | RF005. |

### 5. Serviços (/services)
- Mapeamento: RF015, UC004.

| ID | Descrição | Pré-condições | Passos | Resultado Esperado | Critério |
|----|-----------|----------------|--------|---------------------|----------|
| TC_SRV_01 | Listar serviços | Logado como client/employee. | 1. GET /services. | 200, lista. | RF015. |
| TC_SRV_02 | Adicionar serviço | Logado como client. | 1. POST /services. | 201. | RF015. |
| TC_SRV_03 | Atualizar serviço | Logado. | 1. PUT /services/{id}. | 200. | RF015. |
| TC_SRV_04 | Remover serviço | Logado. | 1. DELETE /services/{id}. | 204. | RF015. |
| TC_SRV_05 | Acesso negado (add como employee) | Logado como employee. | 1. POST /services. | 403. | RNF003. |
| TC_SRV_06 | Edge: Duração 0 | Logado. | 1. POST com duration 0. | 400 Inválido. | RF015. |

### 6. Agendamentos (/appointments)
- Mapeamento: RF004, RF003, RF010, RF016, RF017, RF018, UC003, UC004, UC010.

| ID | Descrição | Pré-condições | Passos | Resultado Esperado | Critério |
|----|-----------|----------------|--------|---------------------|----------|
| TC_APPT_01 | Listar agendamentos | Logado como client. | 1. GET /appointments com filtros. | 200, lista filtrada. | RF004, UC004. |
| TC_APPT_02 | Criar agendamento manual | Logado, sem conflito. | 1. POST /appointments. | 201, verificado conflito. | RF004. |
| TC_APPT_03 | Conflito de horário | Horário ocupado. | 1. POST /appointments. | 409 Conflito. | RF003. |
| TC_APPT_04 | Atualizar agendamento | Logado. | 1. PUT /appointments/{id}. | 200. | RF004. |
| TC_APPT_05 | Cancelar agendamento | Logado. | 1. DELETE /appointments/{id}. | 204, notificação enviada. | RF010. |
| TC_APPT_06 | Exportar agendamentos | Logado como client. | 1. GET /appointments/export. | 200, arquivo CSV/PDF. | RF016. |
| TC_APPT_07 | Acesso limitado (employee) | Logado como employee. | 1. GET /appointments. | 200, apenas próprios. | RF004. |
| TC_APPT_08 | Performance: 100 agendamentos simultâneos | - | Simular. | Sem atrasos (RNF002). | RNF005. |
| TC_APPT_09 | Edge: Data passada | Logado. | 1. POST com date passada. | 400 Inválido. | RF017. |

### 7. Clientes Finais (/customers)
- Mapeamento: RF006, UC006.

| ID | Descrição | Pré-condições | Passos | Resultado Esperado | Critério |
|----|-----------|----------------|--------|---------------------|----------|
| TC_CUST_01 | Listar clientes finais | Logado como client. | 1. GET /customers. | 200, com análises. | RF006. |
| TC_CUST_02 | Obter detalhes cliente | Logado. | 1. GET /customers/{id}. | 200. | RF006. |
| TC_CUST_03 | Acesso negado (employee) | Logado como employee. | 1. GET /customers. | 403. | RNF003. |
| TC_CUST_04 | Edge: Busca sem resultados | Logado. | 1. GET com search inválido. | 200, lista vazia. | RF006. |

### 8. Estoque (/stock) - Apenas Plano Ouro
- Mapeamento: RF007, UC007, RN04.

| ID | Descrição | Pré-condições | Passos | Resultado Esperado | Critério |
|----|-----------|----------------|--------|---------------------|----------|
| TC_STOCK_01 | Listar produtos | Logado como client Ouro. | 1. GET /stock/products. | 200. | RF007. |
| TC_STOCK_02 | Adicionar produto | Logado Ouro. | 1. POST /stock/products. | 201. | RF007. |
| TC_STOCK_03 | Atualizar produto | Logado. | 1. PUT /stock/products/{id}. | 200. | RF007. |
| TC_STOCK_04 | Remover produto | Logado. | 1. DELETE /stock/products/{id}. | 204. | RF007. |
| TC_STOCK_05 | Registrar movimento | Logado. | 1. POST /stock/movements. | 201. | RF007. |
| TC_STOCK_06 | Acesso negado (plano inferior) | Logado Prata. | 1. GET /stock/products. | 403 Plano não permite. | RN04. |
| TC_STOCK_07 | Edge: Quantidade negativa | Logado. | 1. POST movimento com qty negativa. | 400 Inválido. | RF007. |

### 9. Relatórios Contábeis (/reports)
- Mapeamento: RF008, RF016, UC008.

| ID | Descrição | Pré-condições | Passos | Resultado Esperado | Critério |
|----|-----------|----------------|--------|---------------------|----------|
| TC_REP_01 | Gerar relatório financeiro | Logado como client. | 1. GET /reports/financial com period. | 200, métricas calculadas. | RF008. |
| TC_REP_02 | Exportar relatório | Logado. | 1. GET /reports/export. | 200, arquivo. | RF016. |
| TC_REP_03 | Acesso negado (employee) | Logado employee. | 1. GET /reports/financial. | 403. | RNF003. |
| TC_REP_04 | Edge: Período sem dados | Logado. | 1. GET com datas vazias. | 200, zeros/ vazio. | RF008. |

### 10. Mensagens Customizáveis (/marketing)
- Mapeamento: RF009, RF021, UC009, RN03-04 (Prata/Ouro).

| ID | Descrição | Pré-condições | Passos | Resultado Esperado | Critério |
|----|-----------|----------------|--------|---------------------|----------|
| TC_MKT_01 | Enviar mensagem | Logado Prata/Ouro. | 1. POST /marketing/messages. | 201, enviadas via WhatsApp. | RF009. |
| TC_MKT_02 | Plano negado (Bronze) | Logado Bronze. | 1. POST /marketing/messages. | 403 Plano não permite. | RN02. |
| TC_MKT_03 | Edge: Segmento vazio | Logado. | 1. POST sem usuários. | 400 Inválido. | RF021. |

### 11. Notificações (/notifications)
- Mapeamento: RF010, UC010.

| ID | Descrição | Pré-condições | Passos | Resultado Esperado | Critério |
|----|-----------|----------------|--------|---------------------|----------|
| TC_NOT_01 | Enviar lembrete manual | Logado client/employee. | 1. POST /notifications/reminders. | 200 Enviado. | RF010. |
| TC_NOT_02 | Acesso negado | Sem login. | 1. POST. | 401. | RNF003. |
| TC_NOT_03 | Edge: Appointment inexistente | Logado. | 1. POST com id inválido. | 404 Não encontrado. | RF010. |

### 12. Integrações Externas (/integrations) - Internal
- Mapeamento: RF003, RF012, UC003, RF014.

| ID | Descrição | Pré-condições | Passos | Resultado Esperado | Critério |
|----|-----------|----------------|--------|---------------------|----------|
| TC_INT_01 | Webhook WhatsApp (agendamento) | Payload mock válido. | 1. POST /integrations/whatsapp/webhook. | 200, agendamento criado no DB. | RF003. |
| TC_INT_02 | Webhook pagamento | Payload mock aprovado. | 1. POST /integrations/payment/webhook. | 200, plano ativado. | RF014. |
| TC_INT_03 | Payload inválido | Payload corrompido. | 1. POST webhook. | 400 Inválido. | RNF007. |
| TC_INT_04 | Segurança: Acesso não internal | Sem auth. | 1. POST. | 401/403. | RNF003. |

### 13. Administração (/admin)
- Mapeamento: RF013, RF023, UC013.

| ID | Descrição | Pré-condições | Passos | Resultado Esperado | Critério |
|----|-----------|----------------|--------|---------------------|----------|
| TC_ADMIN_01 | Listar clientes | Logado admin. | 1. GET /admin/clients. | 200, lista com métricas. | RF013. |
| TC_ADMIN_02 | Obter métricas globais | Logado. | 1. GET /admin/metrics. | 200 (churn, total_clients). | RF023. |
| TC_ADMIN_03 | Atualizar cliente | Logado. | 1. PUT /admin/clients/{id}. | 200 Atualizado. | RF013. |
| TC_ADMIN_04 | Acesso negado (client) | Logado client. | 1. GET /admin/clients. | 403. | RNF003. |
| TC_ADMIN_05 | Edge: Métricas com 0 clientes | Logado. | 1. GET /admin/metrics. | 200, zeros. | RF023. |

## Aprovação e Métricas de Sucesso

- Cobertura: Medida por tools (ex.: pytest-cov >80%).
- Defeitos: Classificados por severidade (crítico: bloqueia UC; alto: afeta RF; médio/baixo).
- Aprovação: Assinatura de stakeholders após fase de aceitação.
- Métricas: Taxa de falhas <5%, tempo de resposta médio <3s, uptime 98% em testes.