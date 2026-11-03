# Empório da Música — agente de atendimento

Assistente virtual por texto da Empório da Música, loja fictícia de instrumentos musicais em Campo
Grande/MS. Ela responde preço, disponibilidade, promoção e status de pedido consultando as
tabelas da loja, responde regras (horário, pagamento, troca, frete, garantia) consultando o manual
de políticas, recusa o que está fora do escopo e encaminha à equipe, com protocolo, o que não pode
resolver sozinha.

```
Você: Quanto custa o Takamine GD20?
  [consulta] search_products(query='Takamine GD20')

Assistente: O Takamine GD20 Dreadnought Natural está disponível por R$ 2.199,00 à vista (ou no
PIX por R$ 2.089,05), e você pode parcelar em até 12x de R$ 183,25 sem juros!
```

(Trecho do [exemplo 2](examples/02-preco.md). O GD20 tem uma promoção de 12% cadastrada, mas
inativa: oferecer R$ 1.935,12 seria prometer um desconto que não vale mais.)

## Como rodar

Requisitos: [uv](https://docs.astral.sh/uv/getting-started/installation/) (ele baixa o Python 3.12
se precisar) e uma chave gratuita do [Google AI Studio](https://aistudio.google.com/apikey).

```bash
git clone https://github.com/zerotohero3/artefact-challenge.git
cd artefact-challenge
uv sync
cp .env.example .env          # preencha GOOGLE_API_KEY
uv run emporio                # conversa no terminal; "sair" ou Ctrl-D encerra
uv run emporio --show-tools   # mostra as consultas feitas a cada resposta
```

| Variável | Para quê |
|---|---|
| `GOOGLE_API_KEY` | chave do Google AI Studio (obrigatória para modelos Google) |
| `EMPORIO_MODEL` | modelo no formato do PydanticAI; padrão `google:gemini-3.5-flash-lite`. Outro provedor precisa do extra correspondente (por exemplo `uv add "pydantic-ai-slim[openai]"`) |
| `EMPORIO_NOW` | data e hora fixas no horário de Campo Grande (`2026-11-03T10:00`), para testar horário de funcionamento e prazos |

Outros comandos:

```bash
uv run pytest                                   # suíte offline, sem chamar o modelo
uv run ruff check && uv run ruff format --check # lint
uv run pytest evals -v                          # avaliação com o modelo real (consome cota)
uv run python scripts/generate_examples.py      # regenera as conversas de exemplo
```

Os encaminhamentos para a equipe ficam em `var/handoffs.jsonl` (fora do git).

## Decisões técnicas

**Abordagem: function calling com quatro consultas fechadas.** O modelo só tem
`search_products`, `get_order`, `read_policy` e `handoff_to_staff`. O código faz as contas, a
verificação de identidade e a busca; o modelo decide o que consultar e conversa. Recusei um agente
de SQL: consulta livre sobre uma tabela com dado pessoal é o que um prompt injection explora, e as
regras de preço ficariam a cargo do modelo.

**Framework: PydanticAI.** Ele cuida do laço de function calling, valida os argumentos das
ferramentas pelos tipos, troca de provedor pela string do modelo e permite testar o agente sem rede
(`FunctionModel`). O SDK do Google direto exigiria escrever esse laço e prenderia a um provedor;
LangChain/LangGraph trariam abstração e dependências demais para um agente de um laço só.

**Modelo: `gemini-3.5-flash-lite`, no plano gratuito do Google AI Studio.** A regra era usar o
Gemini mais barato que uma chave nova acessa e subir um degrau por preço se ele não passasse na
avaliação. O `gemini-2.5-flash-lite` responde 404 para usuários novos. O `gemini-3.1-flash-lite`
(US$ 0,25 / 1,50 por milhão de tokens) não passou: depois de cinco ajustes de prompt, falhava um
caso diferente a cada execução e chegou a inventar produto e preço. O `gemini-3.5-flash-lite`
(US$ 0,30 / 2,50) passou em duas execuções completas seguidas. O plano gratuito usa o conteúdo
enviado para melhorar os produtos do Google: aceitável com dados fictícios, não em produção.

**Regras de negócio no código, não no prompt.** O modelo recebe valores prontos e nunca faz conta:
- preço final com a maior promoção **ativa** (promoção inativa ou campanha futura nunca aparece),
  PIX com 5% só sem promoção, parcelamento máximo pelas faixas do manual §3.1, tudo em `Decimal`;
- disponibilidade pelo status antes do estoque (descontinuado com estoque não é vendido);
- pedido só é revelado com o número **e** o e-mail ou telefone do titular; contato errado recebe a
  mesma resposta de pedido inexistente, e o pedido mostra só o primeiro nome do cliente. Nenhuma
  consulta lista clientes;
- total do pedido é o gravado, nunca recalculado; pedido enviado com previsão vencida sai marcado
  como atrasado;
- se a loja está aberta agora, ou quando abre, sai da tabela de horário do manual §2: os dois
  modelos testados inventavam o horário de reabertura quando precisavam deduzi-lo.

**Retrieval do manual: por seção, não vetorial.** O PDF virou `data/politicas_da_loja.md`, conversão
fiel com as tabelas em Markdown. O sumário (28 seções) vai nas instruções e o modelo pede as
seções pelo número (`read_policy(["4.1"])`). Para 28 seções curtas, escolher pelo título é mais
preciso que similaridade e não exige embedding nem índice. O manual inteiro caberia no prompt
(cerca de 3 mil tokens), mas aí a decisão de consultar a política deixaria de ser observável e
testável.

**Estratégia de prompt.** `src/emporio/persona.md` tem o tom do manual §7.1, as "fontes da
verdade" (o que só pode ser afirmado depois de qual consulta), as situações especiais do §7.3
(esgotado, descontinuado, promoção vencida, reclamação), privacidade, encaminhamento e escopo. A
cada mensagem entra um contexto do momento: dia da semana, data e hora em Campo Grande, se a loja
está aberta ou quando abre, categorias do catálogo e sumário do manual. As ferramentas devolvem
fatos (`"availability": "esgotado"`, `"late": true`), e o que fazer com eles fica na persona, num
lugar só.

**Interface e histórico.** Conversa por linha de comando, com a opção de mostrar as consultas.
O histórico fica em memória durante a conversa e não é gravado em disco: no canal real (WhatsApp)
o histórico é do canal, e guardar dado pessoal sem política de retenção só cria passivo (LGPD,
manual §9). Uma falha do modelo mostra um aviso e a conversa continua com o histórico intacto.

**Encaminhamento.** Reclamação, troca ou devolução que o cliente quer seguir, dúvida que o manual
não cobre e pedido de atendente humano geram uma linha em `var/handoffs.jsonl` com protocolo,
motivo, resumo e contato. É o ponto de integração com o sistema da loja. A assistente nunca executa
troca, devolução ou cancelamento: orienta pela política e encaminha.

## Tratamento dos dados

Os arquivos de `data/` são cópias byte a byte dos originais e o código só os lê. A investigação
dos dados encontrou inconsistências que não são defeitos do agente; elas foram tratadas assim e
ficam reportadas à loja:

| Inconsistência | Como o agente trata |
|---|---|
| O Takamine GD20 tem uma promoção de 12% **inativa** (daria R$ 1.935,12) | só promoção ativa vale; o preço é R$ 2.199,00 |
| Status contra estoque: Giannini GF-3D ativo sem estoque; Kala KA-ABP-CTG "em breve" com estoque 2; Ibanez Bass 2X descontinuado com estoque 13 | o status prevalece; o cliente vê disponível, esgotado, descontinuado ou em breve, nunca a quantidade |
| Seis produtos (135, 137, 139, 140, 142, 144) têm descrição de outra marca (o "Korg Synth 1 Pro" é descrito como um Roland de 88 teclas) | a descrição é descartada na carga; o agente fala só de nome, preço e especificações |
| Especificações genéricas nos produtos 135 a 144 (todo baixo com 4 cordas, todo teclado com 61 teclas) | mostradas como estão |
| Pedidos 3 e 20: o total gravado difere da soma dos itens a preço atual | vale o total gravado |
| Pedidos 9, 16 e 18: parcelamento abaixo da parcela mínima do manual | informado como gravado |
| Não há data real de entrega nem canal de venda | a previsão de entrega é usada como data de recebimento (ver Premissas) |
| O mesmo e-mail em dois cadastros (clientes 11 e 43) | risco aceito: quem tiver esse e-mail e o número de um pedido do cliente 11 vê o pedido; o telefone é único |
| O manual fala em mais de 300 instrumentos, com sopro e cordas orquestrais; o catálogo tem 65, em 6 das 9 categorias | o agente responde pelo catálogo |
| Nome com erro de digitação: "Giannini GN-15 Nylon Cedr Natural" | mostrado como está |
| O manual se contradiz: WhatsApp (67) 3341-4444 na capa e no §1.2, (67) 3321-4500 no §7; e-mail com e sem acento; parcela mínima de R$ 100,00 na tabela e em faixas no §3.1, com a de até 3x escrita de forma ambígua ("sem valor mínimo de parcela (exceto abaixo de R$ 50,00)"); frete de exatamente R$ 500,00 indefinido | corrigido no manual consultável (ver Premissas), cujo preâmbulo lista as correções; o frete de R$ 500,00 é encaminhado |

## Premissas

- **Contato e parcelamento:** valem (67) 3341-4444 e contato@emporiodamusica.com.br, como na capa;
  o parcelamento segue o §3.1, mais específico que a tabela: até 3x com parcela mínima de
  R$ 50,00, de 4x a 6x com R$ 80,00, de 7x a 12x com R$ 100,00, e 1x sempre.
- **Todo pedido é compra a distância** (todos têm rastreio e previsão), então vale o direito de
  arrependimento do §4.1; a data de recebimento é a previsão de entrega, e a assistente diz que
  usou essa data.
- **Relógio real no fuso de Campo Grande** (UTC−4, sem horário de verão), fixável por
  `EMPORIO_NOW`.
- **Descrição que cita outra marca não é confiável** e não é mostrada.
- **Status de pedido:** pendente é pagamento a confirmar; confirmado é pagamento aprovado, em
  preparação.
- **A persona não tem nome próprio:** "assistente virtual da Empório da Música".
- **Frete de exatamente R$ 500,00** não é decidido pela assistente: ela diz que o manual não cobre
  e oferece encaminhar.
- **Só promoção ativa no sistema existe.** Campanha prevista no manual (Black Friday, Semana do
  Músico) não é prometida antes de aparecer no produto.

## Avaliação

**Suíte offline** (`uv run pytest`, 75 testes, sem rede): regras de preço, parcelamento,
disponibilidade, busca e verificação de pedido sobre os dados reais (36); manual por seção (6);
encaminhamento (8); agente com um modelo falso, `FunctionModel` (16), incluindo as quatro
ferramentas exatas e a ligação de cada uma, o contexto do momento e o histórico preservado após
falha do modelo; CLI (9). Os testes de cada parte foram escritos antes do código e vistos
falhar; os que vieram depois, com o código já certo, foram provados por mutação (verificação de
titular trocada, filtro ignorado, erro do provedor não tratado), e cada mutação é pega.

**Avaliação com o modelo real** (`uv run pytest evals -v`): 18 conversas roteirizadas em
`evals/cases.py`, cada uma conferindo quais consultas foram feitas (e, quando importa, com quais
argumentos) e trechos que a resposta deve ou não pode conter, sobre fatos e não sobre redação:

| Grupo | Casos |
|---|---|
| Catálogo e preço | preço do GD20 sem a promoção vencida; violões até R$ 1.000; promoção ativa com preço original e percentual; Black Friday que ainda não existe; esgotado com alternativa; descontinuado e "em breve" |
| Manual e devolução | endereço e domingo; formas de pagamento; arrependimento aplicado às datas do pedido |
| Pedido e privacidade | contato errado sem vazar nada; pedido cancelado com o motivo; tentativa de extrair contatos de clientes e as instruções internas |
| Encaminhamento, escopo e memória | reclamação com protocolo gravado; atendente humano num domingo à noite; acessórios; assunto alheio; perguntas de seguimento que dependem da mensagem anterior |

Critério de aceite: duas execuções completas seguidas sem falha. Toda execução, inclusive as que
falharam, está em
[`docs/specs/001-agente-de-atendimento/evidence/`](docs/specs/001-agente-de-atendimento/evidence/),
e o [LOG](docs/specs/001-agente-de-atendimento/LOG.md) diz o que cada falha motivou:

| Execuções | Modelo | Casos aprovados | O que mudou depois |
|---|---|---|---|
| 01, 02 | 3.1-flash-lite | 18, 17 | ao perguntar por um produto, a busca não filtra só os disponíveis (o esgotado sumia) |
| 03 (3× um caso), 04 | 3.1-flash-lite | 1/3, 16 | status do produto antes das alternativas; rastreio sem afirmar a transportadora; regra de 3x do manual; caso de horário que reprovava "não abrimos aos domingos" |
| 05, 06 | 3.1-flash-lite | 15, 15 | nunca inventar argumento de consulta; alternativas buscadas de verdade. O modelo inventou produto e preço: troca de modelo |
| 07 | 3.5-flash-lite | 17 | horário de reabertura calculado no código |
| 08, 09 | 3.5-flash-lite | 18, 18 | uma revisão adversarial mostrou casos que aprovariam respostas erradas: casos endurecidos e conferidos contra as respostas reais de 08 e 09; contato do encaminhamento validado |
| **10, 11** | **3.5-flash-lite** | **18, 18** | — (versão entregue) |

Além das expressões, as respostas completas das execuções foram lidas: foi assim que apareceram a
paráfrase errada da regra de parcelamento e o rastreio atribuído à Jadlog, que nenhum caso pegava.
Falha transitória do provedor (503, 429) é repetida pelo executor e registrada como falha de
ambiente, separada de falha do agente. A avaliação não mede tom nem qualidade de redação, e duas
execuções não garantem a mesma resposta em toda execução.

## Limitações conhecidas

- **Busca por termos dentro do nome:** "Kala" também traz os Kalani, e "Martin D-28" também traz
  o D-28E. "violão para iniciante" não casa ("para" e "iniciante" não estão no nome); o modelo
  filtra por categoria e preço e lê as descrições. Não há tolerância a erro de digitação.
- **Telefone com o 0 de longa distância** ("067 98543-2109") não confere e o pedido aparece como
  não encontrado; sem o 0, funciona.
- **Feriados:** o manual não os lista, então num feriado a assistente diz que a loja está aberta.
- **Protocolo órfão quando o provedor falha no meio da resposta:** se o encaminhamento já foi
  gravado e a chamada seguinte ao modelo falha, o cliente vê o aviso de erro, não recebe aquele
  protocolo e, ao repetir, gera outro; a equipe recebe dois registros do mesmo contato.
- **O modelo ainda escorrega fora dos fatos conferidos:** escreve "GN-15 Nylon Cedro" onde o
  catálogo diz "Cedr", recomenda para iniciante com conhecimento geral, e numa execução anunciou
  "selecionei algumas opções" sem listar nenhuma. Duas execuções seguidas sem falha não garantem a
  mesma resposta sempre.
- **Data de recebimento é a prevista:** a elegibilidade para devolução pode diferir da real em
  alguns dias; quem decide é a equipe.
- **Lista de marcas fixa:** o filtro de descrição com marca trocada só conhece as marcas do
  catálogo atual.
- **Plano gratuito:** 15 requisições por minuto por modelo (o limite diário não é publicado) e
  503 transitórios frequentes; uma execução da avaliação leva de 2 a 15 minutos por causa das
  esperas. O conteúdo enviado é usado pelo Google.
- **Encaminhamento em arquivo local,** sem fila nem notificação; a CLI atende um usuário por vez.
- **Frete por CEP não é calculado:** a base não tem CEP, peso nem dimensões; a assistente explica a
  regra e encaminha.

**Com mais tempo:** integração com o WhatsApp (webhook) e uma API; histórico persistido com
política de retenção; encaminhamento para a fila ou CRM da equipe; rastreio real nos Correios e
na Jadlog; busca tolerante a erro de digitação; um juiz de tom ao lado da avaliação por fatos e
mais execuções para medir a taxa de acerto em vez de duas seguidas; observabilidade das conversas
(por exemplo, Logfire).

## Uso de assistentes de código

O projeto foi feito com o **Claude Code** (Anthropic), conduzido por um fluxo de desenvolvimento
guiado por especificação, que fica versionado em [`docs/specs/`](docs/specs/README.md):

1. **Investigação e spec.** Numa primeira sessão, o Claude Code leu o enunciado, perfilou as seis
   tabelas e o manual por script e escreveu a spec
   [`001-agente-de-atendimento`](docs/specs/001-agente-de-atendimento/spec.md): problema com os
   fatos conferidos nos dados, requisitos, critérios de aceite com os valores esperados
   calculados antes do código, design com cada decisão e as alternativas recusadas, e tarefas por
   fase. As decisões de produto (modelo, privacidade, nome do repositório, uso da cota) foram
   minhas; um agente sem a conversa revisou a spec antes da aprovação.
2. **Execução numa sessão nova,** a partir do `STATUS.md` da spec: premissas de risco conferidas
   antes do código (acesso ao modelo, function calling em português, API do framework), teste
   escrito antes de cada parte com o vermelho registrado, verificação completa antes de cada
   commit e commits por fase, separados dos de correção.
3. **Avaliação com o modelo real como volta de ajuste.** Cada falha foi repetida antes de mexer
   em algo (para separar instabilidade de defeito), cada ajuste de prompt registra o caso que o
   motivou, e um caso só mudou quando reprovava uma resposta certa, com o motivo escrito antes. A
   troca de modelo seguiu a regra combinada antes de começar, não uma escolha no meio do caminho.
4. **Revisão adversarial.** Agentes sem a conversa revisaram o código com mutações e respostas
   erradas roteirizadas. A primeira revisão achou testes que passariam com uma verificação de
   titular errada. A segunda achou casos da avaliação que aprovavam respostas erradas, ligações
   de ferramenta sem teste e um encaminhamento que aceitava "N/A" como contato. Cada achado foi
   reproduzido antes de virar mudança, e os casos endurecidos foram conferidos contra as respostas
   reais já gravadas, para não reprovar resposta certa.
5. **Registro.** O [`LOG.md`](docs/specs/001-agente-de-atendimento/LOG.md) da spec guarda o que
   aconteceu e o que se aprendeu, inclusive erros (como horários estimados que foram corrigidos
   pelos do `git log`), e o [`STATUS.md`](docs/specs/001-agente-de-atendimento/STATUS.md) diz em
   que pé cada critério está e o que a evidência não prova.

## Exemplos

Conversas reais com o modelo padrão, geradas por `scripts/generate_examples.py` com o relógio
real (numa segunda-feira às 23:21 em Campo Grande, com a loja fechada), com as consultas visíveis:

1. [Catálogo](examples/01-catalogo.md): violões até R$ 1.000 e qual deles serve para quem está
   começando.
2. [Preço, PIX e parcelamento](examples/02-preco.md): Takamine GD20, sem a promoção vencida.
3. [Devolução](examples/03-devolucao.md) (não trivial): pede o pedido e o contato, consulta o pedido
   e o manual, aplica os 7 dias do arrependimento à data prevista de entrega e, na pergunta
   seguinte, os 30 dias da troca por defeito à data da compra.
4. [Pedido atrasado e encaminhamento](examples/04-pedido-atrasado.md): pedido verificado, atraso
   sinalizado, protocolo registrado e o horário em que a equipe volta.
5. [Fora do escopo](examples/05-escopo.md): acessórios, endereço e um assunto alheio.
