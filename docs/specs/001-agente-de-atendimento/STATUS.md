# STATUS 001 — Agente de atendimento

**Estado:** em execução · **Atualizado em:** 2026-11-03
**Progresso:** 20/31 tarefas · **Fase atual:** 4 — avaliação, modelo e exemplos
**Próximo passo:** T-21 (commit e push da Fase 4); depois o aceite manual do dono (T-22).
**Bloqueios:** nenhum.
**Aceite pendente:** —
**Último estado verificado:** `1518447` publicado; depois dele, ajustes de persona, do caso `endereco-horario` e da regra de 3x no manual (não commitados); ruff limpo, 57 testes passando · 2026-11-03 00:02

## Como retomar

Fases 0 a 3 feitas (LOG, 2026-11-02). Avaliação até agora: 01 18/18, 02 17/18, 03 (repetições de
`esgotado`) 1/3, 04 16/18, 05 15/18, 06 15/18 (3.1, com fabricação de preço), 07 17/18 (3.5); cada falha e cada ajuste estão no LOG. Modelo padrão: `google:gemini-3.5-flash-lite` (P-07). A avaliação
roda com `uv run pytest evals -v` e cada execução vai para
`evidence/evals-NN-<modelo>.txt` (a `evals-00-esqueleto-...` é o vermelho da T-15 e não conta).
Falha transitória do provedor é repetida pelo executor e impressa como "falha de ambiente". Estado
real: `git log --oneline` e `git status`. Prazo: 2026-11-03 23:59; horários de corte em tasks.md,
"Antes de começar".

## Lacunas

- **T-03 `[~]`: limite diário do plano gratuito não conhecido.** O limite por minuto apareceu no
  detalhe do 429 durante a avaliação: 15 requisições por minuto, por modelo (`gemini-3.1-flash-lite`
  e `gemini-3.5-flash-lite`). O diário não aparece na API nem na documentação; só no painel do AI
  Studio, que exige o login do dono. Uma execução completa da avaliação faz cerca de 50 a 70
  requisições e esbarra no limite por minuto, que o executor absorve com espera.

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
| CA-10 | ✅ validado com o modelo real | execuções 08 e 09 seguidas, 6/6 casos do grupo em cada (`evidence/evals-08-...`, `evals-09-...`); todas as execuções gravadas | estabilidade além de duas execuções; qualidade de redação |
| CA-11 | ✅ validado com o modelo real | execuções 08 e 09, 3/3 casos do grupo em cada | idem; o caso `endereco-horario` foi corrigido duas vezes por reprovar resposta certa (LOG) |
| CA-12 | ✅ validado com o modelo real | execuções 08 e 09, 3/3 casos do grupo em cada | outras formas de prompt injection além das três do caso `extracao` |
| CA-13 | ✅ validado com o modelo real | execuções 08 e 09, 6/6 casos do grupo em cada | feriados (o manual não os lista) |
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
