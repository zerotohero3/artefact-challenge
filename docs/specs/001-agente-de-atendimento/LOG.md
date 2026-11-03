# LOG 001 — Agente de atendimento

## 2026-11-02 — Especificação

**Origem.** Desafio técnico de AI Engineer da Artefact: prototipar, em Python, um agente de
atendimento por texto para a Empório da Música, com README, 3 a 5 conversas de exemplo e
repositório público com histórico de commits real. Entrega até 2026-11-03 23:59.

**O que foi lido.** O enunciado em PDF e na conversão HTML do dono (mesmo conteúdo); as seis
tabelas, perfiladas por script (tipos, duplicatas, chaves estrangeiras, totais contra itens,
promoções por produto, formato dos códigos de rastreio); o manual inteiro (8 páginas, 28 títulos
numerados, 1.753 palavras pela extração do `pdftotext`).

**O que a investigação encontrou e mudou o desenho.** Ver spec §1. Os pontos que viraram decisão:
promoção inativa no produto do enunciado → preço no código (D-04); status contra estoque → status
prevalece (R-04); descrições com marca trocada → busca só no nome (D-09) e P-04; total gravado
diferente da soma → total gravado (R-08); ausência de data real de entrega → P-02; contradições do
manual → P-01 e manual curado (D-03); tabela de clientes com dado pessoal → sem agente de SQL
(D-02) e verificação no código (D-05).

**Números calculados antes do código** (script independente, `Decimal`, meio-para-cima):

- Promoções ativas: Kalani KAL-700T R$ 359,00 −10% = R$ 323,10; Ohana CK-20 R$ 549,00 −20% =
  R$ 439,20; Crafter HT-100 R$ 2.399,00 −18% = R$ 1.967,18; Taylor 110e R$ 5.999,00 −8% =
  R$ 5.519,08.
- Takamine GD20: PIX R$ 2.089,05; com a promoção inativa de 12% daria R$ 1.935,12.
- Parcelamento máximo: 349,90 → 4x 87,48; 2.199,00 → 12x 183,25; 159,90 → 3x 53,30;
  99,90 → 1x; 429,90 → 5x 85,98; 439,20 → 5x 87,84; 11.499,00 → 12x 958,25; 599,00 → 6x 99,83.
- Violões disponíveis com preço final até R$ 1.000: 12 (ids 83, 85, 89, 88, 81, 84, 87, 86, 107,
  82, 91, 112, em ordem de preço); fora por indisponibilidade: 96 (ativo, estoque 0) e 113
  (descontinuado).
- Com o relógio em 2026-11-02: pedido 7, 258 dias desde a previsão de entrega (17/02/2026);
  pedido 8, 247 dias (28/02/2026) e 260 desde o pedido.

**Pesquisa externa (2026-11-02).** Página de preços do AI Studio: `gemini-2.5-flash-lite` é o mais
barato (US$ 0,10 / 0,40), `gemini-3.1-flash-lite` custa US$ 0,25 / 1,50; ambos têm plano gratuito,
e o conteúdo do plano gratuito é usado para melhorar os produtos do Google. Página de modelos: o
acesso ao 2.5-flash-lite é limitado a quem já usava a família 2.5, e a recomendação para projetos
novos é a família 3.5. Limites do plano gratuito: não publicados, só no painel. PydanticAI:
`pydantic-ai-slim[google]`, `google:<modelo>`, `GOOGLE_API_KEY`, `FunctionModel`/`TestModel`.

**Decisões do dono.** Sobre a proposta inteira (PydanticAI, consultas fechadas, manual por seção,
regras no código, verificação de pedido, encaminhamento, CLI, avaliação, premissas P-01 a P-06):
"concordo com tudo". Modelo: "seria o modelo mais barato/básico do google", com chave gratuita do
AI Studio já criada. Prazo: "precisa ser entregue até amanha 23:59". Repositório: "nao existe
ainda repo, voce cria com meu email anonimo. pode ter o agents.md sim".

**Ambiente.** Python 3.14.4 do sistema; `uv` ausente; `gh` autenticado como `zerotohero3`.
Repositório criado com `git init -b main` e `user.email` anônimo do GitHub, configurado só neste
repositório.

## 2026-11-02 — Revisão da spec por agente sem a conversa

Um subagente leu só a pasta da spec, o enunciado e os dados, e recalculou os números por script
próprio: todos os valores da spec, do LOG e dos contratos bateram. Os achados abaixo foram
reproduzidos antes de virar mudança (script sobre os CSVs e teste do `git ls-files`):

- **Busca (alta):** a regra "todo termo no nome" não achava "violão Giannini GF-3D" nem "ukulele
  Ohana CK-20", porque a categoria não está no nome. D-09 passa a aceitar o termo como palavra da
  categoria no singular; CA-04 ganhou esses casos.
- **Avaliação (alta):** casos que passariam com um agente errado (`seguimento-pix` conferia todas as
  respostas e o 1º turno já traz o PIX; `devolucao` não exigia a negativa; `acessorio` aceitava
  "temos cordas para seu instrumento"; `extracao` não podia falhar) e casos que reprovariam um
  agente correto (`violoes-ate-1000` exigia o 5º item da lista; "atras" e "7 dias" sem
  alternativas). A tabela foi reescrita: checagens na última resposta por padrão, expressões com
  alternativas, argumentos e número mínimo de chamadas, relógio por caso. Entraram
  `campanha-futura` (Black Friday inativa de 30% no Tagima Woodstock daria R$ 629,30),
  `fora-do-expediente` (domingo 20:00) e `seguimento-pedido` (memória); `extracao` passou a pedir
  telefone de cliente e as instruções internas.
- **Critério que não falhava:** "todos passam numa execução registrada" permitia repetir até sair
  verde. Agora: duas execuções completas seguidas, com toda execução gravada.
- **Fechamento fora de ordem:** a conferência no repositório público vinha depois do push final e
  não provava visibilidade pública. Ela passou para antes do STATUS final (T-28), com checagem de
  visibilidade e clone sem credencial; entrou a T-31 (o dono envia o link).
- **Prazo:** horários de corte em 2026-11-03 e corte do RS-04 com gatilho.
- **Cota do plano gratuito:** T-03 anota limites por minuto e por dia e o orçamento; Q-02 pede ao
  dono a saída autorizada se a cota diária acabar.
- **Manual:** CA-08 vale para a saída da consulta (o preâmbulo cita as correções), confere a
  remissão da tabela de pagamento à 3.1 e que pedir "1" não traz "10"; P-08 para frete de
  R$ 500,00 exatos; verificação da T-10 trocada por diff de palavras contra o `pdftotext`.
- **Checklist:** `git ls-files` escapa caminhos com acento, e o grep pela pasta do enunciado
  voltava vazio mesmo com ela no índice (reproduzido em repositório descartável); trocado por
  `git -c core.quotePath=false ls-files`.
- **Dados:** a troca de marca atinge 6 produtos (135, 137, 139, 140, 142, 144), não os 10 da faixa;
  as especificações dessas linhas são genéricas. P-04 reescrita e D-17 descarta a descrição na
  carga (CA-20). Pedidos 9, 16 e 18 têm parcelamento abaixo do mínimo do §3.1 (spec §1).
- **Privacidade nos casos:** o telefone (67) 99123-4567 usado no caso de reclamação é de uma cliente
  da base; trocado por (67) 98888-7777, conferido como ausente.
- **Menores:** R-10 deixa claro que o encaminhamento é quando o cliente quer seguir; CA-21 cobre
  "nada gravado em disco"; casos de avaliação escritos antes da persona (T-15); arredondamento da
  parcela explicado em D-04; seção "Premissas" no README (CA-17 com títulos exatos).

## 2026-11-02 — Aprovação

O dono aprovou a spec ("1. aprovo.") e respondeu às questões:

- Q-01: "nome vai continuar sendo o que ja é, o nome do repo é: artefact-challenge." A criação do
  repositório público fica para a T-09, confirmada com ele.
- Q-02: "ok, mas nao vai acabar, só não abusar." Virou a decisão de usar a cota com parcimônia
  (spec §5).
- `.env`: "crie o .env que eu só colo a chave no arquivo depois." Criado na raiz com
  `GOOGLE_API_KEY=` vazio e permissão 600, ignorado pelo git (`git check-ignore`).
- Execução: "executo em outra sessao a spec." A spec é commitada sozinha, antes do código.

## 2026-11-02 — Execução, Fase 0

**Retomada (22:57).** Estado real igual ao STATUS: só a spec commitada (`62b7747`), árvore limpa,
`uv` ausente. A chave já estava no `.env` (`grep -c '^GOOGLE_API_KEY=.' .env` → 1;
`git check-ignore .env` → `.env`), então a T-02 está cumprida pelo dono. A revisão para execução
não achou divergência entre design e código, porque ainda não há código; as divergências da API do
framework estão abaixo.

**T-01.** `uv` 0.13.6 instalado no usuário pelo instalador oficial (`~/.local/bin`, sem mexer no
PATH, que já o tinha). `uv python find 3.12` falhou antes de `uv python install 3.12`; depois,
CPython 3.12.16 gerenciado pelo uv.

**T-03 (23:00).** Script descartável fora do repositório, chave enviada só por cabeçalho:
- `gemini-2.5-flash-lite` → 404: "This model models/gemini-2.5-flash-lite is no longer available to
  new users. Please update your code to use models/gemini-3.5-flash-lite".
- `gemini-3.1-flash-lite` → 200, respondeu "ok" (8 tokens).
- **Modelo padrão pela regra de D-13: `gemini-3.1-flash-lite`.** A listagem de modelos da chave
  inclui `gemini-3.5-flash-lite`, o próximo da escada de P-07.
- **Limites: não obtidos.** As respostas não trazem cabeçalho de limite; a página de limites do AI
  Studio (consultada agora) diz que os limites são por projeto, variam por modelo e "can be viewed
  in Google AI Studio", sem publicar números do plano gratuito; o RPD zera à meia-noite do
  Pacífico. O painel exige o login do dono. Não estourei a cota de propósito para ler o limite no
  erro 429 (Q-02: "só não abusar"). Se um 429 aparecer, os detalhes do erro trazem o limite
  violado e ele entra aqui.
- **Orçamento estimado sem o limite diário:** uma pergunta com uma consulta custou 2 requisições e
  ≈ 370 tokens de entrada com instruções mínimas (T-04); com a persona e o sumário, a estimativa é
  de 2 a 3 mil tokens por requisição. Uma execução completa da avaliação (18 casos, 24 mensagens)
  ≈ 50 a 70 requisições. Quantas cabem por dia fica sem resposta até haver o RPD.

**T-04 (23:00–23:02).** PydanticAI 2.65.0 com `gemini-3.1-flash-lite`, ferramenta falsa
`get_price` e três perguntas em português. As duas primeiras tentativas caíram já na primeira
pergunta com **503 UNAVAILABLE** ("This model is currently experiencing high demand"); uma chamada
crua logo depois respondeu 200, e a terceira tentativa passou nas três:
- "Quanto custa o violão Takamine GD20?" → `get_price(product='violão Takamine GD20')` → "custa
  R$ 2.199,00".
- "Qual é o preço do Yamaha C40?" → `get_price(product='Yamaha C40')` → "R$ 599,00".
- "Me fala o valor do ukulele Ohana CK-20, por favor." → `get_price(product='ukulele Ohana CK-20')`
  → "R$ 439,20".
RS-01 não se confirmou. O 503 transitório mostra que a falha do provedor é real e frequente, o que
reforça a R-14 e entra no RS-02.

**T-05.** `pydantic-ai-slim[google]` instalado resolveu para **2.65.0** (google-genai 2.34.0),
versão maior que a documentação lida na especificação. Conferido por script offline:
- `@agent.instructions` com `RunContext[Deps]` funciona; `FunctionModel` recebe as instruções da
  execução em `AgentInfo.instructions` ("Hoje é 02/11/2026.").
- `Agent.override(model=FunctionModel(...))`, `run_sync(..., message_history=...)`,
  `all_messages()` e `new_messages()` funcionam; `ToolCallPart` traz `tool_name` e `args`.
- **Construir `Agent('google:...')` sem `GOOGLE_API_KEY` levanta `UserError`.** Com
  `defer_model_check=True` a construção passa e o erro só vem na execução. É o que o design
  precisava responder ("como evitar que construir o agente exija a chave").
- `models.ALLOW_MODEL_REQUESTS = False` bloqueia a requisição real com `RuntimeError` ("Model
  requests are not allowed"), mas só depois de o provedor ser criado: sem chave, o erro que aparece
  é o da chave.
- Os nomes das ferramentas registradas aparecem por API pública em `AgentInfo.function_tools`
  (útil para CA-06 sem atributo privado).
- **A 2.x imprime um banner no primeiro `run` do processo** num terminal; ele é suprimido sob o
  pytest, em CI e com `pydantic_ai.BANNER_ENABLED = False`. A CLI precisa desligá-lo.
- `result.usage` virou propriedade (`.usage()` emite `PydanticAIDeprecationWarning`).
- Erro do modelo: o 503 chega como `pydantic_ai.exceptions.ModelUnavailableError`; um erro
  levantado dentro do `FunctionModel` propaga sem embrulho.
Design atualizado: ponto de partida (versão e fatos acima), D-13 (padrão decidido) e RS-02 (503).

## 2026-11-02 — Execução, Fase 1

**T-06.** `pyproject.toml` (sem `authors`: o modelo do `uv init` punha o e-mail pessoal),
`.python-version` 3.12, `.env.example` com o padrão `google:gemini-3.1-flash-lite`,
`src/emporio/__init__.py`. Lock: pydantic-ai-slim 2.65.0, ruff 0.17.3, pytest 9.2.0. O ruff 0.17
checa e formata também `docs/specs/check_spec.py` (cópia do verificador da convenção) e os blocos
Python dentro do `design.md`; `docs` saiu do ruff (`extend-exclude`), porque é documentação do
processo, não código do produto. `uv sync`, `ruff check` e `ruff format --check` com saída 0;
`uv run pytest` sai com 5 (nenhum teste coletado, esperado antes da T-07). Dados copiados para
`data/` com nomes curtos; SHA-256 dos originais, iguais aos das cópias:

```
7a7901e16c8c6357a956031ada45a6fd6a4cc9bd7bc1edc05448cc55b01b0a9e  categories.csv
1cd724dc86eac6258913cc890abf23d3893c57a99c9325ebfb91dfad3c7b0f37  customers.csv
7656eb681821d48e0c932f61d3188309b955c25446578235f2d8e69604b0f0bc  order_items.csv
deb9c2480605d8d22117d569f0045fd156c5e9a58ffeebb847ff61b3b9512fd5  orders.csv
78d911d96ee891abb163b6c858e895025aa530ab27d0290540f05d5098377c12  products.csv
cbe08c7e91b00437c0c00a7ef1486deba73de52d23e3f97f51a7dbd557d759e0  promotions.csv
b7527f96896929f4ba929de117651c6717e25b7a3b92b34bc54d5ba32f6156f7  politicas_da_loja.pdf
```

**T-07 — vermelho.** `tests/test_store.py` com os valores da spec §4, contra `store.py` em
esqueleto (busca vazia, pedido não encontrado, parcelamento vazio). Primeira rodada: 31 falhas e
1 aprovação; 4 falhas eram `KeyError` (acesso a campo de pedido e de produto antes de conferir que
veio) e o teste de sufixo curto de telefone passava contra o esqueleto, porque só conferia a recusa.
Ajuste: cada teste confere primeiro que o pedido ou o produto veio, e o teste do sufixo passou a
cobrir a fronteira dos dois lados (8 dígitos aceito, 7 recusado). Segunda rodada:
**32 falhas, todas `AssertionError`**, pelo motivo esperado (esqueleto sem dado).
Além dos CA, entraram dois testes do contrato da busca (D-09): faixa de preço sobre o preço final
(entre R$ 1.900 e R$ 2.000 só o Crafter HT-100, R$ 1.967,18 com a promoção; o Yamaha APX600 de
R$ 1.899,00 fica fora) e categoria desconhecida listando as válidas.

**T-08 — verde.** `src/emporio/store.py`: 32 testes passando; `ruff check` e
`ruff format --check` limpos. Conferido por comando além dos testes: entre os 65 produtos, só
135, 137, 139, 140, 142 e 144 perdem a descrição (D-17); promoções ativas e parcelamentos batem
com os números calculados na especificação (Kalani R$ 323,10; Crafter R$ 1.967,18; Taylor
R$ 5.519,08; 429,90 → 5x 85,98; 439,20 → 5x 87,84; 11.499,00 → 12x 958,25); a busca por
"violões" com teto de R$ 1.000 só entre disponíveis também dá 12. Escolhas locais: a busca devolve
os itens empatados em preço por id; `days_since_estimated_delivery` e `estimated_delivery` vêm
`null` quando não há previsão, para o formato do objeto não variar.

**T-09 (23:35).** O dono confirmou a criação ("Pode criar e publicar"), depois de ver a lista de
commits, o e-mail anônimo e a conferência de que nada proibido estava no índice (0 arquivos sob
`.env`, `var/`, `.agents/` e a pasta do enunciado). `gh repo create zerotohero3/artefact-challenge
--public --source . --remote origin --push`; `gh repo view --json visibility` → `PUBLIC`;
`origin/main` = `62172c3`. Uma revisão adversarial da Fase 1, por agente sem a conversa, roda em
paralelo à Fase 2; o que ela achar volta para cá.

## 2026-11-02 — Execução, Fase 2

**T-10.** `data/politicas_da_loja.md` escrito à mão a partir do `pdftotext -layout`: títulos
`## N.` e `### N.N`, as quatro tabelas em Markdown, listas, e um preâmbulo (antes da seção 1, fora
de qualquer seção) com as três correções de P-01. Cabeçalho e rodapé de página ("Empório da Música
Manual de Políticas e Procedimentos", "Página N", o rodapé final) ficaram fora; capa e versão estão
no topo. `grep -cE '^#{2,3} [0-9]' data/politicas_da_loja.md` → 28. Diff de palavras normalizadas
(sem acento, sem pontuação) entre as seções e a extração, por script descartável: 1.631 palavras no
PDF, 1.632 no Markdown, e só duas diferenças, ambas de P-01: "de r 100 00" → "conforme a secao 3 1"
(tabela da seção 3) e "3321 4500" → "3341 4444" (seção 7). A correção do e-mail da 1.2 não aparece
porque a diferença é só o acento, que a normalização apaga; ela está conferida pelo teste da CA-08.

**T-11 — vermelho.** `tests/test_policies.py` (6 testes) e `tests/test_handoff.py` (3), contra
esqueletos: 9 falhas. Uma era `FileNotFoundError` (o teste de acréscimo lia o arquivo antes de
conferir algo); ganhou antes a asserção de protocolos distintos, que é parte do contrato. Segunda
rodada: **9 falhas, todas `AssertionError`**, pelo motivo esperado.

**T-12 — verde.** `src/emporio/policies.py` e `src/emporio/handoff.py`; 41 testes passando, ruff
limpo. Seção pedida com subseções e seção inexistente juntas devolvem o texto das que existem e a
lista das inexistentes no fim (o contrato só descrevia o caso inexistente sozinho).

**Ajuste sem mudança de comportamento (CA-21).** A busca da CA-21 (`open\(|write_text|write_bytes`
em `src`) acharia a leitura dos CSVs (`path.open(...)` na `Store`) e reprovaria o critério sem
haver gravação. A leitura passou a `csv.DictReader(io.StringIO(path.read_text(...)))`; os CSVs só
têm LF (`file data/*.csv`), e a carga completa da `Store` antes e depois é idêntica byte a byte
(repr de produtos, categorias, clientes, pedidos e itens, 43.038 bytes, `cmp` sem diferença).
`git grep` só olha arquivos rastreados: antes do commit, a busca precisa de `--untracked`; com ele,
só `handoff.py` aparece.

## 2026-11-03 — Revisão adversarial da Fase 1

Um agente sem a conversa revisou o commit `62172c3` contra a spec, com mutações do código numa
cópia exportada do commit. Cada achado foi reproduzido aqui antes de virar mudança:

1. **Testes não provavam R-06 (alta).** O código recusava certo, mas as mutações "qualquer cliente
   com esse contato vê o pedido" (IDOR) e "telefone aceito só pelo tamanho" passavam nos 32
   testes, porque o único contato errado testado não existia na base. Reproduzido: 32 verdes com
   cada mutação. Correção: o teste de contato errado passou a usar também o e-mail e o telefone de
   outra cliente real (a do pedido 8) e confere a igualdade com o pedido inexistente para os três.
2. **"Kala" traz Kalani; "Martin D-28" traz o D-28E (média).** Reproduzido (10 resultados para
   "Kala", 3 deles Kalani). É o que a D-09 manda (termo dentro do nome compactado), e trocar por
   palavra inteira quebraria "GD20" contra "GD 20". Fica como custo declarado na D-09; vai para as
   limitações do README.
3. **Pontuação colada ao termo impedia casar a categoria (média-baixa).** "violões, Yamaha", "violões?"
   e "ukuleles." davam 0. O código aplicava o singular ao termo sem compactá-lo, ao contrário da
   D-09. Teste novo (`"violão, Giannini GF-3D?"` → 96) vermelho por asserção antes da correção;
   depois, `singular(compact(term))` e os quatro exemplos dão 7, 7, 35 e 15.
4. **`late` só para pedido enviado não tinha teste (média-baixa).** A mutação que ignora o status
   passava. Teste novo: pedido 7, entregue e com previsão 258 dias atrás, sai com `late` falso.
5. **Regras da D-04 sem teste no produto (baixa).** Testes novos: parcelamento sobre o preço final
   no Ohana (5x de R$ 87,84, número do LOG da especificação), PIX do Yamaha C40 com arredondamento
   meio-para-cima (599,90 × 0,95 = 569,905 → R$ 569,91) e limite de 20 itens com o total de 65. A
   "maior promoção ativa" não tem caso na base (nenhum produto tem duas ativas); ficou sem teste.
6. **O comando da CA-21 falhava no `62172c3` (baixa).** Já resolvido no `14f5a8f` (leitura com
   `read_text`).
7. **Telefone com 0 de longa distância é recusado (baixa).** Reproduzido. Recusa do lado seguro;
   custo declarado na D-05 e limitação no README.
8. **Comentário citava "(P-01)" (mínima).** Contraria o AGENTS.md; o comentário passou a dizer a
   regra do manual.

Prova de que os testes novos pegam o que antes passava: cada mutação (IDOR, telefone pelo
tamanho, `late` sem status, parcela sobre o preço de tabela, arredondamento bancário, sem limite
de 20) reprova exatamente um teste além do de pontuação, que ainda estava vermelho. Depois da
correção: 45 testes passando, ruff limpo. A lista de marcas da D-17 continua sem teste contra
marcas que não são de instrumento ("Aquila", "LR Baggs"); o teste da CA-20 confere os 9 produtos
da faixa e o comando do T-08 confirmou que só 6 dos 65 perdem a descrição.
