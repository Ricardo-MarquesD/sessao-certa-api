# Plano de Entrega - Go-live até o fim do mês

## Objetivo deste plano
Colocar o backend em produção com o mínimo necessário para operar, cobrar e reduzir risco operacional imediato.

Regra de decisão deste mês:
- Entram apenas itens que bloqueiam receita, segurança básica e estabilidade mínima.
- Refatorações de design/arquitetura/otimização ficam para revisão profunda pós-go-live.

## Prioridade 0 - Obrigatório antes de produção (bloqueadores)

1. Autenticação mínima nas rotas críticas
- Escopo: proteger endpoints de agendamento, WhatsApp register/disconnect e Google connect/disconnect.
- Critério de pronto:
  - Toda rota crítica exige token válido.
  - Usuário sem permissão recebe 401/403.
  - Não existe rota de escrita sensível pública.

2. Isolamento de tenant no fluxo de agendamento
- Escopo: impedir acesso por UUID de outro estabelecimento.
- Critério de pronto:
  - Get/Update/Delete de agendamento validam estabelecimento do usuário autenticado.
  - Testes cobrindo tentativa de acesso cross-tenant retornando 403/404.

3. Segredos e credenciais
- Escopo: higiene operacional imediata.
- Critério de pronto:
  - .env continua fora do git.
  - Rotacionar chaves reais usadas (Google, Meta, Stripe, Brevo, webhook token).
  - Ambiente de produção usa variáveis seguras (não hardcoded).

4. Tratamento global de erros (contrato único)
- Escopo: padronizar erro para frontend e suporte.
- Critério de pronto:
  - Handler global implementado.
  - Erros 4xx/5xx seguem formato único com code/message.
  - Não vazar stack trace para cliente.

5. Concorrência de agendamento (evitar double booking)
- Escopo: evitar duas reservas no mesmo horário em corrida simultânea.
- Critério de pronto:
  - Existe proteção transacional/lock/constraint efetiva.
  - Teste concorrente comprovando que não cria dois agendamentos conflitantes.

6. Webhook WhatsApp com validação de origem no POST
- Escopo: impedir webhook falso.
- Critério de pronto:
  - Assinatura/técnica de validação aplicada no POST.
  - Requisição inválida é rejeitada (401/403).

7. Fluxo de autenticação por e-mail (Brevo) ponta a ponta
- Escopo: login real para liberar uso do produto.
- Critério de pronto:
  - Endpoint para iniciar autenticação por e-mail (envio de OTP/link) funcionando.
  - Endpoint para validar OTP/link e emitir token de sessão funcionando.
  - Token expirado/inválido retorna 401 de forma consistente.

8. Cobrança Stripe funcional (checkout + confirmação)
- Escopo: conseguir cobrar e refletir estado de assinatura.
- Critério de pronto:
  - Endpoint para criar sessão de checkout Stripe funcionando.
  - Webhook Stripe implementado com validação de assinatura.
  - Eventos de pagamento atualizam status de assinatura no sistema.

9. Regra de acesso por assinatura ativa
- Escopo: proteger endpoints que geram valor e custo operacional.
- Critério de pronto:
  - Cliente sem assinatura ativa não acessa funcionalidades premium/críticas.
  - Cliente em dia mantém acesso normal.
  - Regra documentada (quem bloqueia e quem não bloqueia).

## Prioridade 1 - Muito importante para operação ainda este mês

1. Healthcheck e readiness
- Critério de pronto:
  - Endpoint de health responde status da aplicação.
  - Endpoint de readiness valida banco.

2. Logging básico estruturado
- Critério de pronto:
  - Logs em pontos críticos: autenticação, criação/edição/cancelamento de agendamento, falhas de integração.
  - Cada erro relevante possui contexto mínimo (endpoint, id de entidade, motivo).

3. Idempotência para criação de agendamento
- Critério de pronto:
  - Repetição da mesma requisição não duplica agendamento.
  - Comportamento documentado para cliente.

4. Retry com backoff em integrações externas
- Escopo: WhatsApp e Google.
- Critério de pronto:
  - Falha transitória tenta novamente de forma controlada.
  - Não entrar em loop infinito.

5. Versionamento de API na borda
- Critério de pronto:
  - Prefixo de versão definido e consistente (ex.: /api/v1).
  - Documentação alinhada ao que está no código.

6. Proteção anti-abuso nos endpoints de autenticação
- Escopo: evitar abuso de envio de e-mail OTP e tentativa massiva de validação.
- Critério de pronto:
  - Limite básico por IP/e-mail para iniciar login.
  - Janela de expiração e tentativas máximas para OTP/link.
  - Retornos previsíveis para bloqueio temporário.

7. Idempotência para webhook Stripe
- Escopo: evitar processamento duplicado de evento de pagamento.
- Critério de pronto:
  - Mesmo event_id não gera dupla atualização de assinatura.
  - Processamento duplicado retorna sucesso seguro sem efeito colateral.

## Prioridade 2 - Pode ir para revisão pós-go-live

1. Refatoração de arquitetura por camadas e commits internos em repositórios.
2. Evolução de fila para broker dedicado (ex.: Celery/Redis).
3. Migrações e estratégia avançada de rollout/rollback com mais governança.
4. Observabilidade completa (métricas, tracing, dashboards, alertas sofisticados).
5. Otimizações de performance e cache fino.
6. Padronização ampla de respostas com envelope único em toda API.

## Plano semanal até o fim do mês

Semana 1:
- Autenticação mínima.
- Fluxo de autenticação por e-mail (Brevo).
- Isolamento de tenant.
- Segredos/rotação.
- Handler global de erros.

Semana 2:
- Concorrência de agendamento.
- Validação webhook POST.
- Stripe checkout + webhook assinado.
- Regra de acesso por assinatura ativa.
- Health/readiness.
- Logging estruturado básico.

Semana 3:
- Idempotência.
- Idempotência do webhook Stripe.
- Retry com backoff integrações.
- Anti-abuso de endpoints de autenticação.
- Versionamento /api/v1 + ajuste de documentação.
- Hardening final e smoke tests.

## Checklist de pronto para go-live

- [ ] Rotas críticas protegidas por autenticação/autorização.
- [ ] Sem acesso cross-tenant em agendamentos.
- [ ] Chaves sensíveis rotacionadas e seguras por ambiente.
- [ ] Erros padronizados sem vazamento técnico.
- [ ] Sem double booking em testes concorrentes.
- [ ] Webhook POST validado.
- [ ] Fluxo de autenticação por e-mail (Brevo) funcional ponta a ponta.
- [ ] Checkout Stripe funcional com webhook assinado e processado.
- [ ] Regra de acesso por assinatura ativa aplicada nos endpoints certos.
- [ ] Health/readiness funcionando.
- [ ] Logs mínimos de operação disponíveis.
- [ ] Idempotência de criação ativa.
- [ ] Idempotência do webhook Stripe ativa.
- [ ] Retries básicos de integração ativos.
- [ ] Endpoints de autenticação protegidos contra abuso.
- [ ] Prefixo de versão aplicado e docs atualizadas.

## Observação estratégica
Este plano é deliberadamente pragmático para gerar receita rápido com risco controlado. Qualidade estrutural profunda fica para a revisão pós-go-live, como decidido.
