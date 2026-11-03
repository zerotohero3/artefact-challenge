# STATUS 001 — Agente de atendimento

**Estado:** aprovada · **Atualizado em:** 2026-11-02
**Progresso:** 0/31 tarefas · **Fase atual:** —
**Próximo passo:** o dono cola a chave no `.env` (T-02); uma sessão nova executa a partir da T-01.
**Bloqueios:** nenhum (a T-03 precisa da chave no `.env`).
**Aceite pendente:** —
**Último estado verificado:** só a spec aprovada commitada, sem código · 2026-11-02

## Como retomar

A spec foi aprovada pelo dono e commitada sozinha; nada de código ainda. A execução será feita
numa sessão nova, a partir da T-01. Leia a spec §1 e §8
(problema e premissas) e o design §3 (D-01 a D-17) e §4 (contratos e casos de avaliação). Estado
real: `git log --oneline` e `git status`. Não comece a Fase 1 sem a Fase 0: o acesso ao modelo
(T-03) decide o modelo padrão. Prazo de entrega: 2026-11-03 23:59; horários de corte em tasks.md,
"Antes de começar".

## Critérios de aceite

| CA | Estado | Evidência | O que a evidência não prova |
|---|---|---|---|
| CA-01 | ⬜ | — | — |
| CA-02 | ⬜ | — | — |
| CA-03 | ⬜ | — | — |
| CA-04 | ⬜ | — | — |
| CA-05 | ⬜ | — | — |
| CA-06 | ⬜ | — | — |
| CA-07 | ⬜ | — | — |
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
| CA-20 | ⬜ | — | — |
| CA-21 | ⬜ | — | — |

## Desvios do design

Nenhum.

## Achados registrados, não corrigidos

As inconsistências dos dados da loja (spec §1) não são defeitos do agente: vão para o README,
seção de tratamento dos dados, como reportadas à loja.

| # | Achado | Registrado em |
|---|---|---|

## Riscos em aberto

RS-01, RS-02, RS-04 e RS-06 (design §10) até a Fase 0 terminar.
