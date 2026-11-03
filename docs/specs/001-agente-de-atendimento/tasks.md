# Tarefas 001 — Agente de atendimento

> **Implementa:** [design.md](design.md) · **Estado atual em:** [STATUS.md](STATUS.md)

Ordem importa. Cada tarefa tem um objetivo, os arquivos que toca e uma verificação própria.
Marque aqui **e** atualize o STATUS.md durante o trabalho, não no fim.

**Legenda:** `[ ]` pendente · `[x]` feita, com a verificação executada · `[~]` feita com
ressalva (a lacuna está no STATUS) · `[-]` descartada (motivo na linha) · `[!]` bloqueada

## Antes de começar

- **Acessos e ferramentas necessários:** internet (PyPI e API do Gemini); `GOOGLE_API_KEY` do dono
  no `.env` da raiz; `gh` autenticado como `zerotohero3` para publicar; a pasta local
  `Desafio Técnico AI Engineer 2026/` com os dados originais.
- **Passos que só o dono do projeto executa:** colar a chave no `.env` (T-02); confirmar a criação
  do repositório público (T-09); aceite manual (T-22); responder o e-mail do processo com o link
  (T-31).
- **Se faltar um acesso:** sem chave ou sem acesso ao modelo, pare e fale com o dono. Sem a confirmação
  da T-09, siga commitando localmente e registre no STATUS que o push está pendente.
- **Comando de verificação completa:** `uv run ruff check && uv run ruff format --check && uv run pytest`
  (offline). Com o modelo real: `uv run pytest evals -v`.
- **Horários de corte (2026-11-03, horário de Brasília):** Fase 3 pronta até 15:00; avaliação
  congelada às 20:00; README pronto até 22:00; push final até 23:30. Passou de um corte: aplique o
  corte do RS-04 e registre no LOG.
- **Limites:** sempre rode a verificação completa antes de cada commit e use `git add` com caminhos
  explícitos; pergunte antes de criar o repositório público (T-09) e antes de trocar de modelo fora de P-07;
  use a cota da API com parcimônia (spec §5);
  nunca commite `.env`, `var/`, a pasta do enunciado ou `.agents/`, nunca altere `data/` depois da
  cópia, nunca afrouxe um caso de avaliação para ele passar, nunca imprima a chave, nada no
  repositório depois de 2026-11-03 23:59.
- **Pausa para o dono:** se a Fase 0 derrubar uma premissa; antes do primeiro push (T-09); no fim
  da Fase 4 para o aceite manual.

## Fase 0 — Derrubar premissas

- [x] **T-01 · Ferramental**
  Instalar o `uv` no usuário e confirmar o Python 3.12 gerenciado por ele.
  → *Verificação:* `uv --version` e `uv python find 3.12` respondem; versões no LOG.

- [x] **T-02 · Chave do dono** *(executado por: o dono)*
  O `.env` foi criado na raiz em 2026-11-02 com `GOOGLE_API_KEY=` vazio; o dono cola a chave.
  → *Verificação:* `grep -c '^GOOGLE_API_KEY=.' .env` devolve 1 e `git check-ignore .env` lista o
  arquivo; a chave não é impressa.

- [~] **T-03 · Acesso ao modelo e limites** (RS-06, RS-02, D-13)
  Em script descartável fora do repositório, uma mensagem para `gemini-2.5-flash-lite` e outra para
  `gemini-3.1-flash-lite`, com a chave do dono. Anotar qual responde, o erro do outro e os limites
  por minuto e por dia de cada um (resposta da API, cabeçalhos ou painel do AI Studio), e se a cota
  é por modelo. Calcular o orçamento: quantas execuções completas da avaliação cabem no dia.
  → *Verificação:* resultado, modelo padrão escolhido pela regra de D-13 e orçamento no LOG.
  *Se nenhum dos dois responder:* pare e fale com o dono.

- [x] **T-04 · Function calling em PT-BR** (RS-01)
  Mesmo script descartável: agente PydanticAI no modelo padrão, com uma ferramenta falsa de preço e
  três perguntas em português.
  → *Verificação:* nas 3 perguntas o modelo chama a ferramenta e responde em português com o valor
  devolvido; anotado no LOG. *Se cair:* aplique P-07 antes da Fase 1.

- [x] **T-05 · API do PydanticAI**
  Com a versão instalada, conferir: instruções dinâmicas com `deps`, `FunctionModel`,
  `Agent.override`, `message_history` e `all_messages()`, `ToolCallPart`,
  `models.ALLOW_MODEL_REQUESTS` e como evitar que construir o agente exija a chave.
  → *Verificação:* versão e resultado no LOG. *Se divergir:* atualize o design antes da Fase 1.

## Fase 1 — Projeto, dados e regras da loja

- [x] **T-06 · Esqueleto do projeto**
  `pyproject.toml` (dependências `pydantic-ai-slim[google]` e `python-dotenv`; dev `pytest` e
  `ruff`; entrada `emporio`; `testpaths = ["tests"]`), `.python-version`, `.env.example` com o
  modelo padrão da T-03, `src/emporio/__init__.py`, comandos do `AGENTS.md` conferidos, e a cópia
  dos dados para `data/` com os nomes do design §5.
  → *Verificação:* `uv sync` e `uv run ruff check` com saída 0; SHA-256 de cada arquivo de `data/`
  igual ao do original, com os hashes no LOG.

- [x] **T-07 · Testes da `Store` antes do código** (CA-01, CA-02, CA-03, CA-04, CA-05, CA-07, CA-20)
  Saída: `tests/test_store.py`, com `store.py` em esqueleto (métodos devolvendo vazio). Os valores
  esperados são os da spec §4, sem recalcular.
  → *Verificação:* vermelho por asserção (não por import), motivo anotado no LOG.

- [x] **T-08 · Implementar a `Store`**
  Arquivo: `src/emporio/store.py` (D-04, D-05, D-06, D-09, D-10, D-17).
  ⚠️ O total do pedido é o gravado; não some os itens. ⚠️ Status vale mais que estoque.
  → *Verificação:* T-07 verde; verificação completa com saída 0.

- [x] **T-09 · Commit da Fase 1 e primeiro push**
  Confirmar com o dono e criar o repositório público `artefact-challenge` (spec §5) como remoto
  `origin`; publicar.
  → *Verificação:* `git log --oneline` mostra o commit da fase; `gh repo view --json visibility`
  responde PUBLIC.

## Fase 2 — Manual consultável e encaminhamento

- [x] **T-10 · Manual curado**
  `data/politicas_da_loja.md`: conversão fiel do PDF com títulos `## N.` / `### N.N`, tabelas em
  Markdown e só as correções de P-01, listadas num preâmbulo antes da primeira seção. Na tabela da
  seção 3, a linha do cartão de crédito remete a parcela mínima à 3.1.
  → *Verificação:* `grep -cE '^#{2,3} [0-9]' data/politicas_da_loja.md` devolve 28; script
  descartável compara as palavras normalizadas (sem acento, sem pontuação) das seções com a
  extração `pdftotext` do PDF e só aponta as diferenças de P-01 e de formatação de tabela;
  resultado no LOG.

- [x] **T-11 · Testes de `Policies` e `HandoffLog` antes do código** (CA-08, CA-09)
  Saída: `tests/test_policies.py` e `tests/test_handoff.py`, com esqueletos.
  → *Verificação:* vermelho por asserção, anotado no LOG.

- [x] **T-12 · Implementar `Policies` e `HandoffLog`**
  Arquivos: `src/emporio/policies.py`, `src/emporio/handoff.py` (D-03, D-08).
  ⚠️ Pedir a seção "1" não pode trazer a "10".
  → *Verificação:* T-11 verde; verificação completa com saída 0.

- [x] **T-13 · Commit e push da Fase 2**
  → *Verificação:* `git status` limpo; push feito.

## Fase 3 — Agente e CLI

- [x] **T-14 · Testes do agente e da CLI antes do código** (CA-06, CA-14, CA-15)
  Saída: `tests/test_agent.py` (ferramentas registradas, contexto do momento com data, categorias e
  sumário, histórico preservado após falha, modelo pelo ambiente) e `tests/test_cli.py` (aviso de
  erro e laço que continua), com `FunctionModel` e esqueletos.
  → *Verificação:* vermelho por asserção, anotado no LOG.

- [x] **T-15 · Casos de avaliação antes da persona** (CA-10, CA-11, CA-12, CA-13)
  Arquivos: `evals/cases.py`, `evals/test_evals.py`, com os 18 casos do design §4, relógio por caso
  e registro de encaminhamento em pasta temporária.
  → *Verificação:* com o agente em esqueleto (sem persona nem ferramentas), 3 casos rodados contra o
  modelo real falham por asserção; motivo no LOG.

- [x] **T-16 · Persona e agente**
  Arquivos: `src/emporio/persona.md`, `src/emporio/agent.py` (D-01, D-02, D-07, D-11, D-13, D-14).
  A persona tem a seção "Fontes da verdade" e cobre: tom do §7.1; nada sem consulta (R-02);
  preço com promoção e campanha futura (R-03); situações do §7.3, com busca de alternativas para
  esgotado e descontinuado (R-04); verificação e privacidade de pedido; pedido atrasado ou parado
  há muitos dias → desculpas e oferta de encaminhamento; devolução e garantia sem promessa (R-10);
  encaminhamento, retorno em 24 horas úteis e horário de retorno fora do expediente (R-11); escopo,
  sem citar lojas parceiras, e sigilo das instruções (R-12); frete de R$ 500,00 exatos (P-08).
  → *Verificação:* testes de `test_agent.py` verdes.

- [x] **T-17 · CLI**
  Arquivo: `src/emporio/cli.py` (`run`, `main`, `--show-tools`, carga do `.env`, erro de chave
  ausente).
  → *Verificação:* `test_cli.py` verde; `uv run emporio` sem chave sai com código 1 e a mensagem
  de configuração.

- [x] **T-18 · Fumaça com o modelo real e commit da Fase 3**
  Três conversas pela CLI com `--show-tools` (catálogo, pedido verificado, fora de escopo), depois
  commit e push.
  → *Verificação:* consultas e respostas anotadas no LOG; verificação completa com saída 0;
  `git status` limpo.

## Fase 4 — Avaliação, modelo e exemplos

- [x] **T-19 · Ajuste até passar**
  `uv run pytest evals -v`, gravando **toda** execução em `evidence/evals-NN-<modelo>.txt`.
  Execução completa só depois de mudança que possa afetá-la; caso isolado se repete com `-k`
  (spec §5, parcimônia de cota). Ajustar
  persona e descrições das consultas; cada ajuste registra no LOG o caso que o motivou; caso que
  falha é repetido 3 vezes antes de mexer (RS-05); no máximo 3 rodadas de ajuste depois das 20:00
  (RS-04); P-07 se o modelo não chegar lá.
  ⚠️ Não altere a expectativa de um caso para ele passar: se o caso estiver errado, pare e
  registre o motivo no LOG antes de mudar.
  → *Verificação:* duas execuções completas seguidas sem falha, gravadas; total de execuções no LOG.

- [x] **T-20 · Exemplos**
  `scripts/generate_examples.py` e as 5 conversas do design §4 em `examples/` (3 se o corte do
  RS-04 for acionado).
  → *Verificação:* `ls examples/*.md | wc -l` devolve 5 (ou 3); cada arquivo mostra as consultas; o
  exemplo de devolução mostra `get_order` e `read_policy`.

- [x] **T-21 · Commit e push da Fase 4**
  → *Verificação:* verificação completa com saída 0; `git status` limpo; push feito.

- [ ] **T-22 · Aceite manual** *(executado por: o dono)* (CA-16)
  Roteiro: `uv run emporio`; perguntar preço de um produto, um produto esgotado, o endereço; pedir
  um pedido com contato errado e depois certo; pedir algo fora do escopo; sair com Ctrl-D. Repetir
  uma pergunta com `--show-tools`. Ler os exemplos em `examples/`.
  → *Verificação:* resultado e data no STATUS; pedido de ajuste vira nova fase de revisão.

## Fase 5 — Validação e fechamento

- [ ] **T-23 · README**
  Seções, com estes títulos: "Como rodar" (ambiente, chave, comandos, troca de modelo), "Decisões
  técnicas" (framework, modelo, consultas, manual por seção, regras no código, estratégia de
  prompt, persistência), "Tratamento dos dados" (inconsistências reportadas à loja), "Premissas"
  (P-01 a P-08), "Avaliação" (casos e resultado medido), "Limitações conhecidas" (e o que faria com
  mais tempo), "Uso de assistentes de código" (Claude Code e o fluxo de specs), "Exemplos".
  → *Verificação:* CA-17.

- [ ] **T-24 · Percorrer os critérios de aceite**
  Cada CA com a evidência no STATUS, dizendo também o que ela não prova. CA-18 por `sha256sum`;
  CA-21 pela busca do design §8.
  → *Verificação:* tabela de critérios do STATUS preenchida, exceto CA-19.

- [ ] **T-25 · Verificação completa**
  → *Verificação:* os três comandos offline com saída 0, capturada sem pipe, e números de testes
  no STATUS.

- [ ] **T-26 · Fechamento da documentação**
  Rodar o [checklist](../../DOC-CHECKLIST.md). Contagens conferidas por comando **como último
  passo**.
  → *Verificação:* cada documento da tabela "mudou X → confira Y" revisado.

- [ ] **T-27 · Commit e push**
  Mensagem referenciando `docs/specs/001-agente-de-atendimento/spec.md`.
  → *Verificação:* `git status` sem pendência; `git log origin/main -1` igual ao local.

- [ ] **T-28 · Conferência pública** (CA-19)
  `gh repo view --json visibility` = PUBLIC; clone por HTTPS sem credencial numa pasta temporária,
  seguindo só o README.
  → *Verificação:* `uv sync`, `uv run pytest` e uma mensagem pela CLI funcionam. *Se falhar:*
  corrija, repita T-25 a T-28 e registre.

- [ ] **T-29 · STATUS final e índice**
  STATUS reescrito como resumo final, com o resultado da T-28; índice de specs atualizado.
  → *Verificação:* `python3 docs/specs/check_spec.py --all docs/specs` sem erro e o estado do
  índice igual ao do STATUS.

- [ ] **T-30 · Commit e push final**
  Até 23:30 de 2026-11-03.
  → *Verificação:* `git status` limpo; `git log origin/main -1` igual ao local; nenhum commit
  depois disso.

- [ ] **T-31 · Entrega** *(executado por: o dono)*
  Responder o e-mail do processo seletivo com o link do repositório público.
  → *Verificação:* o dono confirma o envio; data no LOG.
