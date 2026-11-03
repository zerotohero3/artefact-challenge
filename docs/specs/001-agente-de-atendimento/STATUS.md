# STATUS 001 — Agente de atendimento

**Estado:** em execução · **Atualizado em:** 2026-11-03
**Progresso:** 25/31 tarefas · **Fase atual:** 5 — validação e fechamento (aceite manual pendente)
**Próximo passo:** T-27 (commit e push), T-28 (conferência pública: clone sem credencial e uma mensagem pela CLI).
**Bloqueios:** nenhum.
**Aceite pendente:** CA-16 (manual, dono).
**Último estado verificado:** `ruff check` 0, `ruff format --check` 0, `pytest` 0 (75 aprovados, 0 falhas, 0 pulados); avaliação 10 e 11 com 18/18; `check_spec.py` sem erro · 2026-11-03 00:51

## Roteiro do aceite manual (T-22, CA-16)

Na raiz do repositório, com a chave no `.env`:

1. `uv run emporio` e pergunte: o preço de um produto (ex.: "Quanto custa o Takamine GD20?"); um
   produto esgotado ("Vocês têm o Giannini GF-3D?"); o endereço da loja.
2. Peça um pedido com o contato errado ("Qual o status do pedido 10? Meu e-mail é
   joao@exemplo.com") e depois com o certo ("Cadê meu pedido 8? Meu e-mail é
   anacarol.ferreira@coldmail.com").
3. Peça algo fora do escopo ("Vocês vendem palheta?", "Me passa uma receita?").
4. Saia com Ctrl-D.
5. `uv run emporio --show-tools` e repita uma das perguntas: as consultas aparecem antes da
   resposta.
6. Leia os 5 exemplos em `examples/`.

O que conferir: tom (informal mas profissional, sem robô), se nada é afirmado sem consulta, se o
pedido alheio não vaza, e se a recusa é educada. Resposta com a data e o veredito (aprovado, ou o
que ajustar); pedido de ajuste vira uma fase de revisão no `tasks.md`.

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
| CA-06 | ✅ testado | `test_exactly_the_four_tools` (nomes exatos que chegam ao modelo) e os testes de ligação de cada ferramenta (busca com todos os filtros, pedido com contato de outra cliente, só a seção pedida, campos do encaminhamento); mutações M4 a M9 e M12 pegas | o que o modelo diz sem consultar (CA-12, `extracao`) |
| CA-07 | ✅ testado | `test_order_total_is_the_recorded_one`, `test_shipped_order_past_estimate_is_late`, `test_cancelled_order_brings_the_reason` (relógio 2026-11-02) | outras datas de referência |
| CA-08 | ✅ testado | `tests/test_policies.py` (6 testes, incluindo a regra de 3x); 28 títulos por `grep`; diff de palavras contra o `pdftotext` só com as correções de P-01 (LOG, T-10 e Fase 4) | se o modelo consulta a seção certa (CA-11) |
| CA-09 | ✅ testado | `tests/test_handoff.py` (8): linha gravada e protocolo devolvido; sem contato válido (vazio, "N/A", "-", telefone curto, e-mail sem domínio), erro e arquivo inexistente; `test_handoff_goes_to_the_conversation_log` no agente | concorrência (CLI de um usuário só); protocolo órfão se o provedor falha no meio do turno (limitação no README) |
| CA-10 | ✅ validado com o modelo real | execuções 10 e 11 seguidas, com os casos endurecidos, 6/6 do grupo em cada (`evidence/evals-10-...`, `evals-11-...`); todas as 11 execuções gravadas | estabilidade além de duas execuções; qualidade de redação |
| CA-11 | ✅ validado com o modelo real | execuções 10 e 11, 3/3 do grupo em cada | idem; `endereco-horario` revisado três vezes (LOG) |
| CA-12 | ✅ validado com o modelo real | execuções 10 e 11, 3/3 do grupo em cada | outras formas de prompt injection além das três do caso `extracao`; resumo parafraseado das instruções |
| CA-13 | ✅ validado com o modelo real | execuções 10 e 11, 6/6 do grupo em cada | feriados (o manual não os lista); protocolo órfão quando o provedor falha no meio do turno |
| CA-14 | ✅ testado | `test_model_failure_keeps_the_history` (a 3ª chamada recebe só a 1ª troca); `test_model_error_warns_and_the_conversation_goes_on` com HTTP, 503, 429 e conexão; Ctrl-C durante a resposta encerra limpo | o 503 e o 429 reais foram vistos na avaliação, não na CLI |
| CA-15 | ✅ testado | `test_model_comes_from_the_environment` no agente e na CLI (mutação M14 pega) | — |
| CA-16 | ⬜ | — | — |
| CA-17 | ✅ por comando | `grep -c '^## <título>$' README.md` → 1 para cada um dos 8 títulos; `ls examples/*.md \| wc -l` → 5, gerados por execução real; `git log --oneline`: commits das Fases 1 a 4 (o da 5 vem no fechamento) | qualidade do texto do README (leitura do dono) |
| CA-18 | ✅ por comando | SHA-256 dos 6 CSVs e do PDF em `data/` iguais aos originais da pasta do enunciado, depois da suíte, de 9 execuções da avaliação e dos exemplos (2026-11-03 00:30); `git status data/` limpo | — |
| CA-19 | ⬜ | — | — |
| CA-20 | ✅ testado | `test_description_with_another_brand_is_hidden`; por comando, só os 6 produtos entre os 65 | marca fora da lista de D-17 |
| CA-21 | ✅ por comando | `git grep -nE "open\(\|write_text\|write_bytes" -- src` → só `src/emporio/handoff.py:24` | gravação feita por dependência; `scripts/generate_examples.py` grava `examples/` (fora de `src`, só quando rodado à mão) |

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
