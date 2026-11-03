# STATUS 001 — Agente de atendimento

**Estado:** implementada · **Atualizado em:** 2026-11-03
**Progresso:** 29/31 tarefas · **Fase atual:** 5 — fechada, falta o aceite do dono
**Próximo passo:** o dono faz o aceite manual (roteiro abaixo, T-22) e envia o link (T-31). Aprovado, a spec vai a `concluída` num commit pequeno, se ainda antes das 23:59 de 2026-11-03.
**Bloqueios:** nenhum.
**Aceite pendente:** CA-16 (manual, dono).
**Último estado verificado:** `282a493` publicado e conferido por clone público; `ruff check` 0, `ruff format --check` 0, `pytest` 0 (75 aprovados); avaliação 10 e 11 com 18/18 · 2026-11-03 00:51

## Resultado

O agente de atendimento da Empório da Música está publicado em
https://github.com/zerotohero3/artefact-challenge: quatro consultas fechadas (catálogo, pedido com
verificação do titular, manual por seção, encaminhamento), regras de dinheiro, data, horário e
privacidade no código, persona com as fontes da verdade, CLI, 75 testes offline e uma avaliação de
18 casos com o modelo real que passou em duas execuções seguidas com a versão final. O modelo
padrão é o `gemini-3.5-flash-lite` (P-07), porque o `gemini-3.1-flash-lite` não passou.

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

Tudo que a spec pede está feito, menos o aceite do dono (CA-16) e o envio do link (T-31). Se o
aceite pedir ajuste: nova fase "Revisão de 2026-11-03" no `tasks.md`, verificação completa, e
avaliação de novo só se o ajuste puder afetá-la (duas execuções seguidas, gravadas em
`evidence/`). Nada entra no repositório depois de 2026-11-03 23:59. Estado real: `git log
--oneline` e `git status`.

## Lacunas

- **T-03 `[~]`: limite diário do plano gratuito não conhecido.** O limite por minuto apareceu no
  detalhe do 429: 15 requisições por minuto, por modelo. O diário só aparece no painel do AI
  Studio, que exige o login do dono. As 11 execuções da avaliação e os exemplos não esbarraram
  nele.

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
| CA-16 | ⬜ aceite do dono pendente | roteiro acima, entregue em 2026-11-03 | — |
| CA-17 | ✅ por comando | `grep -c '^## <título>$' README.md` → 1 para cada um dos 8 títulos; `ls examples/*.md \| wc -l` → 5, gerados por execução real; `git log --oneline`: commits de todas as fases (Fase 1 `62172c3`, 2 `14f5a8f`, 3 `1518447`, 4 `1febea0` e `4ffe476`, 5 `282a493`), mais os de correção | qualidade do texto do README (leitura do dono) |
| CA-18 | ✅ por comando | SHA-256 dos 6 CSVs e do PDF em `data/` iguais aos originais da pasta do enunciado, depois da suíte, das 11 execuções da avaliação e dos exemplos (conferido de novo em 2026-11-03 00:51); `git status data/` limpo | — |
| CA-19 | ✅ validado no repositório público | 2026-11-03 00:51: `gh repo view --json visibility` → PUBLIC; clone por HTTPS com `GIT_TERMINAL_PROMPT=0` e sem credential helper, no `282a493`; seguindo só o README: `uv sync` ok, `uv run pytest` 75 aprovados, `uv run emporio --show-tools` respondeu o horário consultando `read_policy(sections=['2'])` | sistemas além do Linux do dono (Windows e macOS não testados) |
| CA-20 | ✅ testado | `test_description_with_another_brand_is_hidden`; por comando, só os 6 produtos entre os 65 | marca fora da lista de D-17 |
| CA-21 | ✅ por comando | `git grep -nE "open\(\|write_text\|write_bytes" -- src` → só `src/emporio/handoff.py:24` | gravação feita por dependência; `scripts/generate_examples.py` grava `examples/` (fora de `src`, só quando rodado à mão) |

## Desvios do design

Nenhuma decisão foi contrariada sem registro; as revisões estão no design, com data e motivo:

- D-07 (revisada em 2026-11-03): o contexto do momento traz se a loja está aberta ou quando abre,
  calculado no código, porque os dois modelos inventavam o horário de reabertura.
- D-08 (revisada em 2026-11-03): o encaminhamento exige um contato válido, não só não vazio.
- D-13 (revisada em 2026-11-03): modelo padrão `gemini-3.5-flash-lite`, pela P-07.
- Design §4 (revisado em 2026-11-03): casos da avaliação endurecidos depois da segunda revisão e
  `endereco-horario` corrigido por reprovar resposta certa.
- Manual curado: a regra de até 3x passou a dizer "parcela mínima de R$ 50,00", aplicação da P-01.

## Aprendizados

- O modelo barato acerta o que é conferido e escorrega no resto: só a leitura completa das
  respostas achou a paráfrase errada da regra de parcelas e o rastreio atribuído à Jadlog.
- Ajuste de prompt para um caso pode soltar outro, e chegou a induzir fabricação de preço: a
  escada de modelo combinada antes (P-07) evitou trocar de modelo por impulso.
- Regra que depende de data ou conta vai para o código (horário da loja), mesmo quando parece
  simples de deduzir.
- Caso de avaliação também tem defeito: dois reprovavam resposta certa e vários aprovavam
  resposta errada; endurecer conferindo contra respostas reais já gravadas evita os dois.
- Horário em LOG se mede com `date`; estimado, ele saiu errado e foi corrigido.

## Achados registrados, não corrigidos

As inconsistências dos dados da loja (spec §1) não são defeitos do agente: estão no README, seção
"Tratamento dos dados", como reportadas à loja.

| # | Achado | Registrado em |
|---|---|---|
| A-01 | Busca por marca traz marca de nome parecido ("Kala" → Kalani) e modelo de nome contido ("Martin D-28" → D-28E) | design D-09 (custo aceito); README, limitações |
| A-02 | Telefone informado com o 0 de longa distância é recusado como pedido não encontrado | design D-05 (custo aceito); README, limitações |
| A-03 | Protocolo órfão: encaminhamento gravado e falha do provedor antes da resposta; o cliente não recebe aquele protocolo e, ao repetir, gera outro | LOG (revisão das Fases 2 a 4); README, limitações |
| A-04 | Feriados: o contexto diz "loja aberta" num feriado (o manual não lista os feriados) | spec §6 (fora de escopo); README, limitações |

## Fora de escopo, com destino

Integração com WhatsApp, API, persistência do histórico, rastreio real, frete por CEP, busca
tolerante a erro de digitação e juiz de tom: README, "Limitações conhecidas" e "Com mais tempo".
