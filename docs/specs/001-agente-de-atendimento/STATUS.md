# STATUS 001 — Agente de atendimento

**Estado:** em execução · **Atualizado em:** 2026-11-02
**Progresso:** 8/31 tarefas · **Fase atual:** 1 — projeto, dados e regras da loja
**Próximo passo:** T-09 (commit da Fase 1; o dono confirma a criação do repositório público).
**Bloqueios:** nenhum.
**Aceite pendente:** —
**Último estado verificado:** `Store` implementada; ruff limpo, 32 testes passando · 2026-11-02 23:25

## Como retomar

Fase 0 feita (LOG, 2026-11-02, "Execução, Fase 0"). Modelo padrão: `google:gemini-3.1-flash-lite`
(o `gemini-2.5-flash-lite` dá 404 para a chave nova). PydanticAI instalado é o 2.65.0: construir o
agente exige `defer_model_check=True` para não pedir a chave, e a CLI precisa desligar o banner
do primeiro `run` (design §1). O provedor devolve 503 transitório com frequência. Estado real:
`git log --oneline` e `git status`. Prazo: 2026-11-03 23:59; horários de corte em tasks.md,
"Antes de começar".

## Lacunas

- **T-03 `[~]`: limites do plano gratuito não obtidos.** Não aparecem na documentação nem nos
  cabeçalhos da API; só no painel do AI Studio, que exige o login do dono. Sem o limite diário, o
  orçamento de execuções da avaliação por dia não foi calculado (estimativa: 50 a 70 requisições
  por execução). Se surgir um 429, o limite violado vem nos detalhes do erro e entra no LOG. O dono
  pode ler os números no painel (AI Studio → projeto → limites) para fechar a lacuna.

## Critérios de aceite

| CA | Estado | Evidência | O que a evidência não prova |
|---|---|---|---|
| CA-01 | ✅ testado | `test_inactive_promotion_is_never_offered`, `test_active_promotion_shows_original_price_and_percent` | o que o modelo diz ao cliente (CA-10) |
| CA-02 | ✅ testado | `test_max_installments` (5 valores) | o que o modelo diz ao cliente (CA-10) |
| CA-03 | ✅ testado | `test_status_prevails_over_stock` (5 produtos) | sugestão de alternativas pelo modelo (CA-10) |
| CA-04 | ✅ testado | `test_available_guitars_up_to_1000`, `test_search_by_name` (6 consultas) | termos com erro de digitação (fora de escopo) |
| CA-05 | ✅ testado | `test_wrong_contact_looks_like_missing_order` (igualdade e ausência de 6 dados), `test_holder_contact_formats`, `test_phone_suffix_needs_eight_digits` | e-mail compartilhado entre clientes 11 e 43 (risco aceito) |
| CA-06 | ⬜ | — | — |
| CA-07 | ✅ testado | `test_order_total_is_the_recorded_one`, `test_shipped_order_past_estimate_is_late`, `test_cancelled_order_brings_the_reason` (relógio 2026-11-02) | outras datas de referência |
| CA-08 | ⬜ | — | — |
| CA-09 | ⬜ | — | — |
| CA-10 | ⬜ | — | — |
| CA-11 | ⬜ | — | — |
| CA-12 | ⬜ | — | — |
| CA-13 | ⬜ | — | — |
| CA-14 | ⬜ | — | — |
| CA-15 | ⬜ | — | — |
| CA-16 | ⬜ | — | — |
| CA-17 | ⬜ | — | — |
| CA-18 | ⬜ | — | — |
| CA-19 | ⬜ | — | — |
| CA-20 | ✅ testado | `test_description_with_another_brand_is_hidden`; por comando, só os 6 produtos entre os 65 | marca fora da lista de D-17 |
| CA-21 | ⬜ | — | — |

## Desvios do design

Nenhum. A Fase 0 completou o design sem contrariar decisão: D-13 ganhou o modelo padrão e o
`defer_model_check`; o ponto de partida e o RS-02 ganharam os fatos da T-03 a T-05.

## Achados registrados, não corrigidos

As inconsistências dos dados da loja (spec §1) não são defeitos do agente: vão para o README,
seção de tratamento dos dados, como reportadas à loja.

| # | Achado | Registrado em |
|---|---|---|

## Riscos em aberto

RS-02 (limites desconhecidos e 503 transitório) e RS-04 (prazo). RS-01 e RS-06 não se confirmaram
na Fase 0; RS-03 virou fato conhecido (API 2.x conferida).
