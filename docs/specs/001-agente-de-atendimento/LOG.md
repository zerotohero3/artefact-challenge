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
