# AGENTS.md

Agente de atendimento por texto da Empório da Música (loja fictícia de instrumentos em Campo
Grande/MS), feito em Python com PydanticAI. Contexto, decisões e estado do trabalho estão nas
specs (abaixo).

## Comandos

```bash
uv sync                          # instala dependências (Python 3.12 via .python-version)
uv run emporio [--show-tools]    # conversa no terminal; precisa de GOOGLE_API_KEY no .env
uv run ruff check && uv run ruff format --check
uv run pytest                    # suíte offline; não chama o modelo
uv run pytest evals -v -rA       # avaliação com o modelo real; consome cota (15 req/min no plano gratuito)
uv run python scripts/generate_examples.py [N ...]  # regrava os exemplos em examples/
```

## Regras de código

- Identificadores, nomes de ferramentas e chaves de retorno em inglês; tudo o que o cliente lê
  (valores, persona, mensagens da CLI) em português do Brasil.
- Comentário só quando explica um porquê que o código não diz. Nada de referência a spec, fase ou
  tarefa no código.
- Dinheiro em `Decimal`; o modelo recebe valores já formatados e nunca faz conta.
- Ferramentas devolvem fatos do domínio; o comportamento da conversa fica em
  `src/emporio/persona.md`.
- Os arquivos de `data/` são cópias dos originais da loja: o código só os lê.
- Toda execução da avaliação é gravada (inclusive as que falham) na pasta `evidence/` da spec em
  andamento; caso de avaliação só muda com o motivo escrito antes, e nunca para afrouxar.

## Git

- Mensagens no formato `tipo(escopo): descrição` em português, com `refs <spec>` no corpo.
- `git add` com caminhos explícitos. Nunca entram no git: `.env`, `var/`, `.agents/` e a pasta do
  enunciado.

## Specs

Mudança que toca segurança, dinheiro, dados do usuário, contrato, schema ou 3+ arquivos ganha uma
spec em `docs/specs/NNN-nome/` antes do código. Convenção e índice:
[docs/specs/README.md](docs/specs/README.md). Ao retomar uma spec, comece pelo STATUS.md dela.
Toda spec termina rodando [docs/DOC-CHECKLIST.md](docs/DOC-CHECKLIST.md).
