# STATUS 001 — Agente de atendimento

**Estado:** em execução · **Atualizado em:** 2026-11-02
**Progresso:** 18/31 tarefas · **Fase atual:** 4 — avaliação, modelo e exemplos
**Próximo passo:** T-19 (primeira execução completa da avaliação, gravada em `evidence/`).
**Bloqueios:** nenhum.
**Aceite pendente:** —
**Último estado verificado:** Fase 3 pronta (agente, persona, CLI; fumaça com o modelo real ok); ruff limpo, 57 testes passando · 2026-11-02 23:27

## Como retomar

Fases 0 a 3 feitas (LOG, 2026-11-02). Modelo padrão: `google:gemini-3.1-flash-lite`. A avaliação
roda com `uv run pytest evals -v` e cada execução vai para
`evidence/evals-NN-<modelo>.txt` (a `evals-00-esqueleto-...` é o vermelho da T-15 e não conta).
Falha transitória do provedor é repetida pelo executor e impressa como "falha de ambiente". Estado
real: `git log --oneline` e `git status`. Prazo: 2026-11-03 23:59; horários de corte em tasks.md,
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
| CA-05 | ✅ testado | `test_wrong_contact_looks_like_missing_order` (contato inexistente e contato de outra cliente real: igualdade e ausência de 6 dados), `test_holder_contact_formats`, `test_phone_suffix_needs_eight_digits` | e-mail compartilhado entre clientes 11 e 43 (risco aceito) |
| CA-06 | ✅ testado | `test_exactly_the_four_tools` (nomes exatos que chegam ao modelo) | o que o modelo diz sem consultar (CA-12, `extracao`) |
| CA-07 | ✅ testado | `test_order_total_is_the_recorded_one`, `test_shipped_order_past_estimate_is_late`, `test_cancelled_order_brings_the_reason` (relógio 2026-11-02) | outras datas de referência |
| CA-08 | ✅ testado | `tests/test_policies.py` (6 testes); 28 títulos por `grep`; diff de palavras contra o `pdftotext` só com as correções de P-01 (LOG, T-10) | se o modelo consulta a seção certa (CA-11) |
| CA-09 | ✅ testado | `tests/test_handoff.py`: linha gravada e protocolo devolvido; sem contato, erro e arquivo inexistente | concorrência (CLI de um usuário só); se o modelo encaminha quando deve (CA-13) |
| CA-10 | ⬜ | — | — |
| CA-11 | ⬜ | — | — |
| CA-12 | ⬜ | — | — |
| CA-13 | ⬜ | — | — |
| CA-14 | ✅ testado | `test_model_failure_keeps_the_history` (a 3ª chamada recebe só a 1ª troca), `test_model_error_warns_and_the_conversation_goes_on` | erros reais do provedor na CLI (vistos só na T-04, fora da CLI) |
| CA-15 | ✅ testado | `test_model_comes_from_the_environment` | — |
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
| A-01 | Busca por marca traz marca de nome parecido ("Kala" → Kalani) e modelo de nome contido ("Martin D-28" → D-28E) | design D-09 (custo aceito); README, limitações (T-23) |
| A-02 | Telefone informado com o 0 de longa distância é recusado como pedido não encontrado | design D-05 (custo aceito); README, limitações (T-23) |

## Riscos em aberto

RS-02 (limites desconhecidos e 503 transitório) e RS-04 (prazo). RS-01 e RS-06 não se confirmaram
na Fase 0; RS-03 virou fato conhecido (API 2.x conferida).
