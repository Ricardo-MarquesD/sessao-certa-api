**Fluxo da State Machine**

O diagrama abaixo descreve o fluxo principal de conversa coberto pelos testes E2E.

```mermaid
graph LR
  A[initial_message: Olá] --> B[service_message: Escolher serviço]
  B --> C[employeee_message: Preferência por funcionário?]
  C -->|Não| D[date_message: Mostrar dias disponíveis]
  D --> E[hour_message: Mostrar horários]
  E --> F[confirm_message: Confirmar?]
  F -->|1 - Confirmar| G[complete_message: Agendamento criado]
  F -->|2 - Desmarcar| H[unmarked_message: Abortado]
  C -->|Escolhe funcionário| D
  A --> I[list_message: Meus agendamentos]
  I --> J[cancel_message: Confirmar cancelamento]
  J --> K[unmarked_message: Cancelado]
```

Observações:
- Entre estados o controlador persiste `context.context_data` (ex.: `service_id`, `available_days`, `available_slots`).
- `confirm_message` revalida conflitos antes de criar o `Scheduling`. Em caso de conflito retorna para `hour_message`.

Arquivo gerado automaticamente por testes E2E.
