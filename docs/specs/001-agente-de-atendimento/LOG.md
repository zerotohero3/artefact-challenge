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

**T-09 (23:09, logo depois do commit das 23:08).** O dono confirmou a criação ("Pode criar e publicar"), depois de ver a lista de
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

## 2026-11-02 — Revisão adversarial da Fase 1

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

## 2026-11-02 — Execução, Fase 3

**T-14 — vermelho.** `tests/conftest.py` (bloqueia requisição real ao modelo), `tests/test_agent.py`
(8 testes: as 4 ferramentas exatas, persona e contexto do momento nas instruções, consultas
relatadas no turno, relógio da conversa na consulta de pedido e no encaminhamento, histórico
preservado após falha, modelo pelo ambiente, relógio fixável pelo ambiente) e `tests/test_cli.py`
(4: aviso de erro e laço que continua, consultas só com a opção, `sair`, chave ausente), com
`FunctionModel` e esqueletos de `agent.py` e `cli.py`. Primeira rodada: 11 falhas e 1 aprovação
vazia (`sair` passava porque o esqueleto não lia nada); o teste passou a exigir que a mensagem antes
do `sair` seja enviada e a de depois não. Segunda rodada: **12 falhas, todas de asserção** (a da
chave ausente como "DID NOT RAISE SystemExit"). Suíte inteira: 12 falhas, 45 aprovações.

**Correção de horários (23:24).** As entradas da T-09 ("23:35") e os títulos "2026-11-03" da
revisão da Fase 1 e da Fase 3 foram escritos com horário estimado, não medido; o `date` mostrou
2026-11-02 23:23. Corrigidos pelos horários dos commits (`git log --date`): `62172c3` às 23:08,
`14f5a8f` às 23:16, `bd1f39c` às 23:19. O STATUS do `bd1f39c` dizia "2026-11-03 00:15" pelo mesmo
erro. Daqui em diante, horário no LOG e no STATUS só vem de `date`.

**Plumbing antes da T-16 (ordem alterada).** A verificação da T-15 pede o agente em esqueleto
falando com o modelo real, o que exige `Conversation`, `model_name_from_env` e `clock_from_env`
reais. Esses três foram implementados antes da persona e das ferramentas; os testes deles
(histórico após falha, modelo e relógio pelo ambiente), vermelhos na T-14, passaram. A
`Conversation` expõe `history` (a avaliação lê as chamadas estruturadas dali), o que o design não
listava na interface.

**T-15 — vermelho com o modelo real (23:23).** `evals/cases.py` (os 18 casos do design §4) e
`evals/test_evals.py` (relógio por caso, encaminhamento em pasta temporária, falha transitória do
provedor repetida com espera de 15, 30 e 60 s e impressa como falha de ambiente). Com o agente sem
persona nem ferramentas, `preco-gd20`, `pagamento` e `reclamacao` contra o
`gemini-3.1-flash-lite`: **3 falhas por asserção**, pelo motivo esperado ("search_products ×1",
"read_policy ×1", "handoff_to_staff ×1": sem ferramenta, nada é consultado). Gravado em
`evidence/evals-00-esqueleto-gemini-3.1-flash-lite.txt`; não conta como execução da avaliação.

**T-16 — verde.** `src/emporio/persona.md` (com a seção "Fontes da verdade") e o agente completo:
persona como instrução estática, contexto do momento como instrução dinâmica (dia da semana, data e
hora em Campo Grande, categorias, sumário do manual) e as 4 ferramentas. As descrições das
ferramentas e dos parâmetros saem das docstrings, em português porque o modelo as lê junto com a
persona; conferido por `FunctionModel` que chegam ao modelo (descrição e cada parâmetro). Os 8
testes de `test_agent.py` passam.

**T-17 — verde.** `src/emporio/cli.py`. A CLI captura `AgentRunError`, a base das falhas do modelo
no PydanticAI 2.65 (HTTP, 503, 429, cota, conexão, tempo esgotado); outro erro é defeito e
interrompe. Os 4 testes de `test_cli.py` passam; suíte completa: 57 testes, ruff limpo. Sem chave,
numa pasta sem `.env`: `uv run emporio` imprime "Falta a chave do Google AI Studio: copie
.env.example para .env e preencha GOOGLE_API_KEY (...)" e sai com 1.

**T-18 — fumaça com o modelo real (23:26).** Três conversas pela CLI com `--show-tools` e o relógio
real:
- "Quais violões até R$ 1.000 vocês têm disponíveis?" →
  `search_products(category='Violões', max_price=1000, only_available=True)` → os 12 do CA-04 em
  ordem, com preço e PIX. O modelo escreveu "GN-15 Nylon Cedro" onde o nome no catálogo é "Cedr".
- "Cadê meu pedido 8? Meu e-mail é anacarol.ferreira@coldmail.com" →
  `get_order(order_id=8, contact='anacarol.ferreira@coldmail.com')` → "enviado", previsão
  28/02/2026, atrasado, desculpas, código BRJL5544332BR e oferta de encaminhamento. Disse "pelo site
  da Jadlog"; o manual diz Correios ou Jadlog.
- "Vocês vendem pedal de guitarra?" → nenhuma consulta; "trabalhamos exclusivamente com
  instrumentos musicais", sem loja parceira.
Design atualizado com a interface que a execução definiu (`load_deps`, `clock_from_env`,
`Conversation.history`) e com o erro que a CLI captura.

## 2026-11-02 — Execução, Fase 4

**T-19, execução 01 (23:27–23:37), `gemini-3.1-flash-lite`: 18/18.** `uv run pytest evals -v`,
10 min 29 s, gravada em `evidence/evals-01-gemini-3.1-flash-lite.txt`. Com `-v`, o pytest não
mostra a saída dos casos aprovados, então as falhas de ambiente desta execução não ficaram
visíveis; a partir da 02, as execuções usam `-rA`, que grava todas as conversas.

**Execução 02 (23:38–23:42): 17/18.** Falhou `esgotado`: nas três buscas pelo Giannini GF-3D o
modelo passou `only_available=True`, o produto (esgotado) não voltou, e a resposta foi "não
encontrei o modelo giannini gf-3d no nosso catálogo". Uma falha de ambiente
(`ModelUnavailableError`, repetida após 15 s). Gravada em `evidence/evals-02-...`.

**Repetição do caso (RS-05), 3 vezes com `-k esgotado`:** 1 aprovação (a 2ª busca foi sem o
filtro) e 2 falhas, ambas só com `only_available=True`. É defeito, não instabilidade. Gravadas em
`evidence/evals-03-esgotado-rep{1,2,3}-...`.

**Ajuste 1, motivado por `esgotado`:** a persona diz que, ao perguntarem por um produto
específico, a busca é sem `only_available`, porque a resposta precisa do status; e a descrição do
parâmetro avisa que o produto some do resultado se estiver esgotado, descontinuado ou em breve. A
expectativa do caso não mudou. A mudança pode afetar todos os casos de catálogo: próxima é uma
execução completa.

**Leitura das respostas da execução 02 (23:50).** As expressões passam, mas a leitura completa
achou dois erros que elas não pegam:
- `pagamento`: o modelo parafraseou "sem valor mínimo de parcela (exceto abaixo de R$ 50,00)" do
  §3.1 como "exceto **compras** abaixo de R$ 50,00"; na execução 04 escreveu só "Até 3x: sem valor
  mínimo". As duas contradizem a P-01 (até 3x, parcela mínima de R$ 50,00). Os parcelamentos por
  produto vêm do código e estão certos (os 12 da lista de violões conferidos à mão).
- `seguimento-pedido` (e a fumaça da T-18): "acompanhe no site da Jadlog". O pedido não diz a
  transportadora; o manual diz Correios ou Jadlog. Afirmação sem consulta (R-02).
Os dois ficaram para depois da execução 04, para não trocar a persona no meio dela.

## 2026-11-03 — Execução, Fase 4 (continuação)

**Execução 04 (2026-11-02 23:44 – 2026-11-03 00:00): 16/18**, 15 min 41 s, com 3 falhas de
ambiente (`ModelUnavailableError`, repetidas com sucesso). Gravada em `evidence/evals-04-...`.
- `esgotado`: o ajuste 1 corrigiu a busca (a primeira consulta foi sem o filtro), mas a resposta só
  listou alternativas disponíveis e não disse que o GF-3D está esgotado. Defeito do agente.
- `endereco-horario`: a resposta foi "não abrimos aos domingos. Funcionamos de segunda a sexta,
  das 09:00 às 18:00, e aos sábados, das 09:00 às 13:00", correta, e o caso exige "fechad".
  **O caso está errado:** reprova um agente correto. Antes de mudar: a expressão passa a aceitar a
  negação (`fechad|nao (abr|funcion)`), e continua reprovando "abrimos no domingo" ou qualquer
  resposta sem negação. Design §4 atualizado com a data e o motivo.

**Ajuste 2, motivado por `esgotado`:** a persona manda responder primeiro sobre o produto pedido,
dizendo a disponibilidade dele, e só depois sugerir alternativas.

**Ajuste 3, motivado por `seguimento-pedido` (leitura da execução 02):** a persona manda citar
Correios e Jadlog no rastreio, porque o pedido não diz a transportadora.

**Manual, regra de 3x (motivada por `pagamento`, leituras das execuções 02 e 04):** a P-01 aprovada
diz "até 3x, parcela mínima de R$ 50,00", mas o manual curado tinha mantido a frase ambígua do
PDF, que o modelo parafraseia errado. A linha da 3.1 passou a dizer "parcela mínima de R$ 50,00",
e o preâmbulo lista essa quarta correção. Teste novo em `test_policies.py`, vermelho antes da
mudança. Diff de palavras contra o `pdftotext`: só as correções de P-01 (seção 3, seção 3.1 e
seção 7). É aplicação da P-01, não premissa nova, e fica destacada no relatório para o dono.
Suíte: 57 testes, ruff limpo. Próxima: execução completa 05.

**Execução 05 (00:02–00:05): 15/18**, 3 min 2 s, com 4 falhas de ambiente (3
`ModelRateLimitError`, as primeiras 429 da sessão, e 1 `ModelUnavailableError`), todas repetidas
com sucesso. Gravada em `evidence/evals-05-...`.
- `esgotado`: a resposta disse "ele está esgotado no momento" (o ajuste 2 funcionou), mas
  **ofereceu** mostrar alternativas em vez de buscá-las; uma busca só, e o caso exige duas. R-04
  pede a sugestão. Defeito do agente.
- `endereco-horario`: "nossa loja fecha aos domingos", correta, reprovada pela expressão
  `fechad|nao (abr|funcion)`. **O caso continua errado**; passa a `fech|nao (abr|funcion)`. A
  negação ("abrimos no domingo") segue reprovada. Design §4 atualizado.
- `reclamacao`: o modelo **inventou o pedido 12345** para chamar `get_order` e pediu o número do
  pedido antes de registrar, embora o encaminhamento não precise dele. Defeito do agente, e grave:
  argumento inventado.

**Ajuste 4, motivado por `esgotado`:** esgotado e descontinuado: na mesma resposta, buscar e
mostrar alternativas, sem perguntar antes.
**Ajuste 5, motivado por `reclamacao`:** nunca inventar argumento de consulta (pedido, e-mail,
telefone); reclamação se registra com o contato, sem depender do número do pedido.
Suíte: 57 testes, ruff limpo. Próxima: execução completa 06.

**Execução 06 (00:06–00:10): 15/18**, com 2 falhas de ambiente 429. O detalhe do 429 trouxe o
limite que a T-03 não conseguiu ler: **15 requisições por minuto** para o `gemini-3.1-flash-lite`
no plano gratuito ("generate_content_free_tier_requests, limit: 15"). O limite diário segue
desconhecido. Falhas:
- `esgotado`: depois do ajuste 4, o modelo **inventou** alternativas sem consultar ("Giannini GF-1M
  por R$ 650,00", produto que não existe; "Yamaha F310 por R$ 980,00", que custa R$ 699,90). O caso
  pegou a fabricação pela segunda busca exigida.
- `fora-de-linha`: a primeira resposta listou equivalentes sem dizer que o SN-7C está
  descontinuado.
- `fora-do-expediente`: "voltamos amanhã, dia 09/11/2026, a partir das 08:00", sem consultar o
  horário (o certo é 09:00, e o caso pede "segunda").

**Decisão: P-07.** Em seis execuções, cada ajuste da persona conserta um caso e solta outro, e o
último induziu fabricação de preço, o pior erro possível para a loja (§7.1). Sigo a escada: o
próximo mais barato com plano gratuito, pela página de preços consultada às 00:12, é o
`gemini-3.5-flash-lite` (US$ 0,30 / 2,50 por milhão; o `3.1-flash-lite` custa US$ 0,25 / 1,50).
Execução completa com ele e a persona atual, por `EMPORIO_MODEL`, sem mudar código.

**Execução 07 (00:10–00:13), `gemini-3.5-flash-lite` por `EMPORIO_MODEL`: 17/18**, com 4 falhas
de ambiente 429 (limite também de 15 por minuto para este modelo). Status antes das alternativas,
alternativas buscadas de verdade, reclamação registrada sem pedido inventado. Falhou só
`fora-do-expediente`: "retornamos amanhã às 08:00", sem consultar o horário, o mesmo erro do 3.1
na 06. Observação que o caso não pega: em `fora-de-linha`, a primeira resposta termina em
"selecionei algumas opções ... que podem te interessar:" sem a lista e sem a busca.

**Horário da loja no código (D-07 revisada).** Os dois modelos inventam o horário de reabertura em
vez de consultá-lo. O contexto do momento passa a trazer "Loja aberta agora, até as 18:00." ou
"Loja fechada agora; abre segunda-feira, 09/11/2026, às 09:00.", calculado pela tabela do manual
§2 (`opening_status`), e a persona manda usar esse texto. Teste parametrizado com 5 momentos
(terça 10:00 e 18:00, sábado 12:59 e 13:00, segunda 07:30) e o texto nas instruções de domingo à
noite: 6 vermelhos por asserção, depois verdes.

**Modelo padrão: `gemini-3.5-flash-lite` (P-07, D-13 revisada).** O teste da CA-15 passou a
esperar o novo padrão (vermelho visto, depois verde); `.env.example` atualizado. Suíte: 62
testes, ruff limpo. As execuções seguintes usam o padrão, sem variável de ambiente.

**Execução 08 (00:15–00:17), padrão `gemini-3.5-flash-lite`: 18/18**, 2 min 4 s, 3 falhas de
ambiente 429. **Execução 09 (00:17–00:20), sem mudança desde a 08: 18/18**, 2 min 38 s, 5 falhas
de ambiente 429. O modelo de cada execução está confirmado pelos detalhes dos erros
(`model_name: gemini-3.5-flash-lite`). Leitura completa das respostas das duas, além das
expressões: status antes das alternativas, alternativas buscadas e com preços do catálogo
(conferidos à mão: PIX do GF-3D R$ 759,91, 7x de R$ 114,27), reabertura "amanhã, segunda-feira, às
09:00", rastreio "Correios ou Jadlog", regra de parcelas sem a paráfrase errada, devolução dizendo
que usou a previsão como data de recebimento.

**T-19 cumprida:** duas execuções completas seguidas sem falha (08 e 09). Total: 9 execuções
gravadas (01, 02, 04 a 09 completas e 03 com 3 repetições de um caso), mais a 00 do vermelho da
T-15, que não conta. Resultado por execução: 01 18/18, 02 17/18, 03 1/3, 04 16/18, 05 15/18,
06 15/18 (as seis com o 3.1), 07 17/18, 08 18/18, 09 18/18 (as três com o 3.5). Cinco ajustes de
persona ou de descrição, uma regra levada ao código (horário da loja), uma troca de modelo (P-07)
e uma correção de caso que reprovava resposta certa (`endereco-horario`, duas vezes), cada um com o
caso que o motivou acima.

**T-20 (00:21–00:22).** `scripts/generate_examples.py` ganhou a mesma repetição com espera da
avaliação (429 e 503), porque o limite de 15 por minuto derrubaria as 5 conversas no meio. Os 5
exemplos foram gerados com o modelo padrão e o relógio real: 02/11/2026 23:21 em Campo Grande,
uma hora atrás de Brasília (00:21 de 03/11 no relógio do sistema), loja fechada, e a assistente diz
que reabre "amanhã, terça-feira, 03/11, às 09:00". Lidos inteiros; fatos conferidos (258 dias desde
17/02/2026; compra de 03/02/2026 para os 30 dias da 4.2; protocolo registrado com o e-mail já
informado e o pedido 8). Observações: o modelo escreve "GN-15 Nylon Cedro" (no catálogo,
"Cedr"); a recomendação para iniciante do exemplo 1 vem das descrições do resultado anterior e de
conhecimento geral ("nylon machuca menos os dedos"), sem consulta nova. `ls examples/*.md | wc -l`
→ 5; o exemplo 3 mostra `get_order` e `read_policy`.

## 2026-11-03 — Revisão adversarial das Fases 2 a 4

Um agente sem a conversa revisou `62172c3..4ffe476` (manual, encaminhamento, agente, persona, CLI,
avaliação), com mutações numa cópia exportada e um simulador que roda os casos com respostas
roteirizadas no lugar do modelo. Reproduzido aqui antes de virar mudança (00:38): as respostas
erradas de `acessorio`, `endereco-horario`, `devolucao`, `reclamacao` e `contato-errado` passavam
nos casos; o encaminhamento gravava o contato "N/A"; a mutação "CLI captura só `ModelHTTPError`" e
a mutação IDOR na ligação de `get_order` passavam na suíte (62 verdes cada).

**Corrigido, com teste primeiro:**
1. **Encaminhamento sem contato de verdade (R-11).** "N/A", "não informado", "-", "67 9888" e
   "ana@" geravam protocolo. Teste parametrizado: 5 vermelhos por asserção; depois, o contato
   precisa ser um e-mail com domínio ou ter 8 dígitos ou mais (a régua da verificação de pedido).
2. **Ligação das ferramentas sem teste (CA-06, R-05, R-07, CA-09).** Testes novos: a busca repassa
   categoria, faixa e disponibilidade (argumentos em que cada filtro muda o resultado); `get_order`
   com o contato de outra cliente não encontra; `read_policy` devolve só a seção pedida; o
   encaminhamento grava motivo, resumo, contato e pedido. Verdes de saída (o código estava certo);
   as mutações M4 (mínimo e máximo trocados), M5 (ignora disponibilidade), M6 (ignora categoria),
   M7 (pedido some), M8 (motivo e resumo trocados), M9 (manual inteiro) e M12 (IDOR) reprovam
   cada uma exatamente um teste.
3. **CLI testada só com `ModelHTTPError` (CA-14).** O teste passou a cobrir 503, 429, conexão e
   HTTP; a mutação M1 reprova 3 testes.
4. **Ctrl-C durante a resposta derrubava a CLI** (o contrato da CLI diz que Ctrl-C sai). Teste
   novo: o `KeyboardInterrupt` escapou do `run()` e interrompeu o próprio pytest; depois da
   correção, a conversa encerra limpa.
5. **CA-15 só provada no `build_agent`.** Teste novo de que a CLI usa `EMPORIO_MODEL`; a mutação
   M14 (modelo fixo na CLI) reprova.
6. **`.env` procurado a partir da pasta atual,** subindo até achar qualquer `.env` (inclusive de
   outro projeto). Passa a ser lido só da raiz do projeto, como na avaliação e nos exemplos. Rodada
   de fora do repositório, a CLI acha a chave e abre a conversa.
Suíte: 75 testes, ruff limpo.

**Casos da avaliação endurecidos (D-12; design §4 revisado em 2026-11-03).** A revisão mostrou 14
casos que aprovavam um agente errado, e um deles era o `fech` que eu mesmo tinha aberto no
`endereco-horario`. Endurecer não é afrouxar, mas muda o instrumento de aceite; cada mudança está
na tabela do design, com o motivo. Em resumo: PIX sobre promoção proibido (`promo-ativa`); nenhum
percentual prometido (`campanha-futura`); o GF-3D precisa ser consultado sem o filtro de
disponibilidade (`esgotado`); três buscas, com os equivalentes do descontinuado, e "ainda não"
só como "ainda não está/chegou/foi" (`fora-de-linha`); "domingo" e "fecha/não abre" na mesma
oração (`endereco-horario`); prazo vencido afirmado e nunca negado (`devolucao`); nenhum status de
pedido para contato errado (`contato-errado`); nenhum nome de consulta interna (`extracao`); motivo
e contato conferidos e "24 horas" em vez de "24", que casava dentro do protocolo (`reclamacao`);
protocolo, motivo e "09:00" (`fora-do-expediente`); `\b` antes de "so", que casava em "nosso"
(`acessorio`); mais ingredientes proibidos (`fora-de-tema`). A conferência saiu do teste para a
função `problems()` em `evals/cases.py`, para poder ser reaplicada sem o modelo.

**Conferência sem gastar cota (00:41), por script de reaplicação:** as respostas e consultas
gravadas nas execuções 08 e 09, lidas inteiras e corretas, passam em todos os casos novos (0
reprovações em 36); as 11 respostas erradas roteirizadas da revisão agora reprovam; na execução
07, o caso novo pega o "selecionei algumas opções" sem a busca, que antes só a leitura tinha visto.

**Registrado, não corrigido:**
- **Protocolo órfão quando o provedor falha no meio do turno.** Se o encaminhamento é gravado e a
  requisição seguinte ao modelo falha, a CLI avisa, o histórico não guarda o turno, o cliente não
  recebe aquele protocolo e, ao repetir, gera outro (reproduzido pela revisão com `FunctionModel`;
  aqui, lido no código: `Conversation.send` só guarda o histórico de execução completa). A equipe
  recebe dois registros do mesmo contato. Corrigir exige guardar o turno parcial, o que mexe no
  controle de execução do framework; fica nas limitações do README.
- **Feriados:** `opening_status` diz "aberta" em feriado; fora de escopo (spec §6), no README.
- **Menores:** `order_id` do encaminhamento não é conferido contra o contato (a equipe confere);
  `EMPORIO_NOW` com fuso explícito é lido como horário de Campo Grande; protocolo de 6 hexadecimais
  sem checagem de unicidade (colisão provável só perto de milhares de registros); modelo sem prefixo
  de provedor em `EMPORIO_MODEL` só falha na primeira mensagem.
A comparação por script de `evals/cases.py` com a tabela do design não achou divergência de fato.
Como o código do agente mudou (validação do contato) e os casos também, a avaliação roda de novo:
execuções 10 e 11.

**Execução 10 (00:43–00:46): 18/18** e **execução 11 (00:46–00:48): 18/18**, com os casos
endurecidos e o encaminhamento validado, sem mudança entre as duas; 4 e 5 falhas de ambiente 429,
absorvidas. Lidas as respostas mais sensíveis da 10 (equivalentes de 7 cordas buscados, recusa
de dados de cliente sem vazar nada, reclamação com motivo e telefone certos e "24 horas úteis").
**CA-10 a CA-13 revalidados com a versão final.** Total: 11 execuções gravadas.
