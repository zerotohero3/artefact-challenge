# Spec 001 — Agente de atendimento

> **Tamanho:** L · **Criada em:** 2026-11-02 · **Estado:** ver [STATUS.md](STATUS.md)
> **Resolve:** demanda nova: desafio técnico de AI Engineer da Artefact (enunciado entregue ao dono, fora do repositório)
> **Relacionada a:** nenhuma

## 1. Problema

A Empório da Música é uma loja fictícia de instrumentos musicais em Campo Grande/MS. Hoje a
equipe atende todos os clientes e está sobrecarregada com perguntas recorrentes: horário, status
de pedido, preço e disponibilidade. A loja entregou seis tabelas da operação (produtos,
categorias, promoções, clientes, pedidos, itens) e o manual interno de políticas (versão 2.1,
8 páginas), e pede um agente de mensagens de texto, em Python, que auxilie a equipe. A entrega é
um repositório público no GitHub até **2026-11-03 23:59**, sem alterações depois disso.

Conferido em 2026-11-02, por script sobre as tabelas e leitura integral do manual:

- **Catálogo:** 65 produtos (62 ativos, 2 descontinuados, 1 "em breve") em 6 das 9 categorias.
  Sopro (madeiras e metais) e Cordas Orquestrais não têm produto; o manual fala em "mais de 300
  instrumentos".
- **Promoções:** 25 cadastradas, 4 ativas. O Takamine GD20, citado no enunciado, custa
  R$ 2.199,00 e tem uma promoção de 12% **inativa**. Oferecer R$ 1.935,12 seria o "desconto que não
  está mais vigente" que o manual proíbe (§7.3) e pode configurar propaganda enganosa (§7.1).
- **Status contra estoque:** o Giannini GF-3D está ativo com estoque 0; o Kala KA-ABP-CTG está
  "em breve" com estoque 2 (e aparece num pedido já entregue); o Ibanez Bass 2X está descontinuado
  com estoque 13.
- **Descrições trocadas:** em 6 produtos (135, 137, 139, 140, 142 e 144) a descrição cita uma
  marca diferente da do nome (o "Korg Synth 1 Pro" é descrito como um Roland de 88 teclas). As
  especificações das linhas 135 a 144 são genéricas (todo baixo com 4 cordas, todo teclado com 61
  teclas) e não servem para desempatar.
- **Pedidos:** 20, de 18 clientes. Em 2 deles (3 e 20) o total gravado difere da soma dos itens a
  preço atual. Em 3 (9, 16 e 18) o parcelamento gravado fica abaixo da parcela mínima do §3.1. Não existe data real de entrega, só a prevista, nem canal de venda. O pedido mais
  recente é de 2026-03-22: pelo relógio real nenhum pedido entregue está dentro dos 7 dias de
  arrependimento, e o pedido 8 ("enviado", previsão 2026-02-28) está atrasado.
- **Clientes:** 50, com nome, telefone, e-mail e cidade. Um mesmo e-mail aparece em dois cadastros
  (clientes 11 e 43).
- **Manual que se contradiz:** telefone/WhatsApp (67) 3341-4444 na capa e no §1.2, mas
  (67) 3321-4500 no §7; e-mail com acento no domínio no §1.2 e sem acento na capa; a tabela de
  pagamento diz "parcela mínima de R$ 100,00" e o §3.1 tem faixas (R$ 50, R$ 80, R$ 100); frete
  grátis "acima de R$ 500,00" e taxa "abaixo de R$ 500,00" deixam R$ 500,00 indefinido.

**O que a solução óbvia não resolve:** um agente que lê as tabelas livremente, ou o manual inteiro
sem critério, responde com fluência e erra justamente nesses pontos: oferece a promoção vencida,
confirma estoque de produto descontinuado, recalcula o total de um pedido, revela o pedido de
outra pessoa a quem só sabe o número.

## 2. Resultado esperado

Antes: toda pergunta passa pela equipe. Depois: o cliente conversa por texto com a assistente
virtual da loja. Ela responde com dado consultado na hora (preço, disponibilidade, promoção,
pedido) ou com a regra do manual (horário, pagamento, troca, frete, garantia), recusa o que está
fora do escopo e entrega à equipe, com protocolo, o que não pode resolver sozinha (reclamação,
devolução, dúvida que o manual não cobre).

## 3. Requisitos

**R-01 · Persona.** A assistente fala sempre em português do Brasil, no tom do manual (§7.1:
informal mas profissional, "um amigo que entende de música") e se apresenta como assistente
virtual da Empório da Música.

**R-02 · Nada sem consulta.** Preço, disponibilidade, promoção, dado de pedido e regra de política
só são afirmados depois de consultados na própria conversa. Se a consulta não traz a informação,
a assistente diz que não tem o dado e oferece encaminhar à equipe; nunca preenche a lacuna.

**R-03 · Preço.** O preço apresentado é o preço final: com promoção ativa, acompanhado do preço
original e do percentual (§6.2). Promoção inativa ou campanha futura nunca é oferecida.
O desconto de 5% no PIX só vale sem promoção. O parcelamento máximo segue o §3.1 (P-01).

**R-04 · Disponibilidade.** Produto ativo com estoque é disponível; ativo sem estoque é esgotado,
com sugestão de alternativas disponíveis; descontinuado não faz mais parte do catálogo, com
sugestão de equivalentes; "em breve" ainda não está à venda. O status prevalece sobre o estoque.

**R-05 · Busca no catálogo.** O cliente encontra produtos por nome, marca ou modelo, por categoria,
por faixa de preço (sobre o preço final) e só entre os disponíveis.

**R-06 · Pedido só para o titular.** Um pedido só é revelado com o número e o e-mail ou telefone do
titular. Se o contato não bater, a resposta é indistinguível da de um pedido inexistente, e
nenhum dado do pedido ou do cliente aparece.

**R-07 · Dados de outros clientes nunca aparecem.** Nenhuma conversa, nem sob instrução do próprio
usuário para ignorar as regras, lista ou revela nome, e-mail ou telefone de outros clientes.

**R-08 · Informações do pedido.** Um pedido verificado mostra status em português, itens, total
gravado (nunca recalculado), forma de pagamento, código de rastreio, previsão de entrega e o
motivo do cancelamento quando houver. Pedido enviado com previsão vencida é sinalizado como
atrasado.

**R-09 · Políticas.** Perguntas sobre a loja, horário, pagamento, troca e devolução, frete,
promoções, garantia e privacidade são respondidas a partir do manual consultado. Quando o manual
não cobre o caso, a assistente diz isso e oferece encaminhamento (§10).

**R-10 · Troca e devolução.** A assistente aplica os prazos do manual às datas do pedido
verificado e diz qual data considerou (P-02). Quando o cliente quer seguir com troca, devolução
ou garantia, ela encaminha à equipe (R-11); nunca promete nem executa a devolução.

**R-11 · Encaminhamento.** Reclamação, pedido de troca ou devolução, dúvida não coberta e pedido de
atendente humano geram um registro para a equipe com motivo, resumo e contato, e o cliente recebe
o número de protocolo. Sem contato, nada é registrado e a assistente pede o contato. Reclamação
informa o retorno em até 24 horas úteis (§7.3); fora do expediente, a assistente informa quando a
equipe volta (§7.1).

**R-12 · Fora de escopo.** Pedido de acessório (cordas, cabos, palhetas, pedais, amplificadores,
cases) é redirecionado explicando que a loja vende só instrumentos, sem inventar loja parceira.
Assunto alheio à loja é recusado com educação, voltando ao atendimento. As instruções internas
não são reveladas.

**R-13 · Memória da conversa.** Dentro de uma conversa, a assistente lembra o que já foi dito
(produto em discussão, pedido já verificado). A conversa não é gravada em disco.

**R-14 · Interface.** O atendimento roda numa conversa por linha de comando, com opção de mostrar
as consultas feitas a cada resposta. Uma falha do modelo (rede, limite de uso) mostra um aviso e
mantém a conversa e o histórico.

**R-15 · Modelo configurável.** O modelo é trocado por configuração, sem mudar código. O padrão é o
definido na §5.

**R-16 · Entregáveis do desafio.** O repositório traz um README com instruções para rodar,
justificativa das decisões, limitações conhecidas e o uso de assistentes de código; de 3 a 5
conversas reais de exemplo, ao menos uma não trivial; e histórico de commits com progresso real.

**R-17 · Dados da loja intactos.** O agente só lê os dados e o manual da loja; nenhuma conversa,
teste ou avaliação os altera.

**R-18 · Descrição não confiável não chega ao cliente.** Descrição de produto que cita uma marca
diferente da do nome não é mostrada (P-04).

## 4. Critérios de aceite

Valores esperados calculados em 2026-11-02 por script independente (ver LOG).

| # | Critério observável | Cobre | Como verificar | Tipo |
|---|---|---|---|---|
| CA-01 | Takamine GD20: preço final R$ 2.199,00, sem promoção, PIX R$ 2.089,05 (nunca R$ 1.935,12). Ohana CK-20: R$ 439,20 com original R$ 549,00 e 20%, sem preço PIX | R-03 | teste da suíte | auto |
| CA-02 | Parcelamento máximo: R$ 349,90 → 4x de R$ 87,48; R$ 599,00 → 6x de R$ 99,83; R$ 2.199,00 → 12x de R$ 183,25; R$ 159,90 → 3x de R$ 53,30; R$ 99,90 → 1x | R-03 | teste da suíte | auto |
| CA-03 | Giannini GF-3D esgotado; Shelby SN-7C descontinuado; Kala KA-ABP-CTG em breve; Ibanez Bass 2X descontinuado apesar do estoque 13; Yamaha C40 disponível | R-04 | teste da suíte | auto |
| CA-04 | Violões disponíveis até R$ 1.000 (preço final) são exatamente 12, em ordem de preço, do Tagima Memphis AC-39 (R$ 429,90) ao Tagima TW-7 (R$ 999,00), sem o GF-3D nem o SN-7C. "Takamine GD20", "takamine gd-20" e "TAKAMINE GD 20" encontram o produto 95; "violão Giannini GF-3D" encontra o 96; "ukulele Ohana CK-20" encontra o 121; "Shelby SN-7C" encontra o 113 | R-05 | teste da suíte | auto |
| CA-05 | Pedido 10 com e-mail errado devolve exatamente a mesma resposta que o pedido 999 **e** a resposta não contém nome, e-mail, telefone, produto nem total do pedido 10; com o e-mail certo ou o telefone em formatos diferentes ("(67) 98543-2109", "67985432109", "+55 67 98543-2109"), o pedido aparece | R-06 | teste da suíte | auto |
| CA-06 | O agente tem exatamente 4 consultas disponíveis (catálogo, pedido, manual, encaminhamento), nenhuma capaz de listar clientes | R-07 | teste da suíte | auto |
| CA-07 | Pedido 3 mostra total R$ 3.450,00 (a soma a preço atual daria R$ 3.498,00); pedido 8, com o relógio em 2026-11-02, aparece como "enviado" e atrasado; pedido 20 traz o motivo do cancelamento | R-08 | teste da suíte | auto |
| CA-08 | O manual consultável tem 28 seções; a 4.1 traz o prazo de 7 dias; pedir a 4 traz de 4.1 a 4.4; pedir a 1 não traz a 10; seção inexistente devolve a lista das válidas; o que a consulta devolve não contém "3321-4500" nem "empóriodamusica", e a tabela da seção 3 remete o mínimo do cartão à 3.1 | R-09 | teste da suíte | auto |
| CA-09 | Encaminhamento com contato grava um registro com protocolo, motivo, resumo e contato **e** devolve o protocolo; sem contato, recusa **e** nada é gravado | R-11 | teste da suíte | auto |
| CA-10 | Avaliação com o modelo real, grupo catálogo e preço (design §4): todos os casos passam em duas execuções completas seguidas | R-02, R-03, R-04, R-05 | suíte de avaliação, com todas as execuções gravadas | real |
| CA-11 | Avaliação, grupo manual e devolução: mesmo critério | R-02, R-09, R-10 | idem | real |
| CA-12 | Avaliação, grupo pedido e privacidade (inclui tentativa de extrair contato de cliente e as instruções internas): mesmo critério | R-06, R-07, R-08, R-12 | idem | real |
| CA-13 | Avaliação, grupo encaminhamento, escopo e memória (inclui encaminhamento fora do expediente e perguntas de seguimento que só se respondem com a mensagem anterior): mesmo critério | R-11, R-12, R-13 | idem | real |
| CA-14 | Uma falha do modelo no meio da conversa mostra um aviso e a próxima mensagem é respondida com o histórico anterior preservado | R-14 | teste da suíte | auto |
| CA-15 | Sem configuração, o agente usa o modelo padrão; com a configuração de modelo definida, usa o configurado | R-15 | teste da suíte | auto |
| CA-16 | O dono conversa pela linha de comando seguindo o roteiro das tarefas, com e sem a opção de mostrar consultas, e lê os exemplos: aprova o tom e o comportamento | R-01, R-13, R-14 | roteiro manual | manual (dono) |
| CA-17 | O README tem as seções "Como rodar", "Decisões técnicas", "Tratamento dos dados", "Premissas", "Avaliação", "Limitações conhecidas", "Uso de assistentes de código" e "Exemplos"; a pasta de exemplos tem de 3 a 5 conversas geradas de execuções reais; há ao menos um commit por fase | R-16 | comando (busca dos títulos, contagem de arquivos, `git log`) | comando |
| CA-18 | Depois da suíte e das avaliações, os arquivos de dados da loja são byte a byte iguais aos originais entregues | R-17 | comando (comparação de hash) | comando |
| CA-19 | O repositório publicado é público e um clone por HTTPS sem credencial, seguindo só o README, instala, passa na suíte e responde a uma mensagem | R-14, R-16 | comando em pasta temporária | real |
| CA-20 | As descrições dos produtos 135, 137, 139, 140, 142 e 144 não aparecem nas consultas; as dos produtos 138, 141 e 143 (mesma marca do nome) aparecem | R-18 | teste da suíte | auto |
| CA-21 | O único ponto do código que grava arquivo é o registro de encaminhamento | R-13, R-17 | comando (busca por escrita de arquivo no código) | comando |

## 5. Decisões de produto

- **Modelo padrão: o Gemini mais barato liberado para uma chave nova do Google AI Studio, no plano
  gratuito.** O dono decidiu em 2026-11-02 ("seria o modelo mais barato/básico do google").
  Alternativa recusada: modelos mais capazes e pagos, por custo. Se ele não passar na avaliação,
  vale P-07.
- **Sem persistência da conversa entre sessões.** Proposto e aceito em 2026-11-02. No canal real
  (WhatsApp) o histórico é do canal, e gravar dado pessoal em disco sem política de retenção só
  cria passivo (LGPD, manual §9).
- **A assistente nunca executa troca, devolução ou cancelamento:** orienta pela política e
  encaminha. Uma decisão com efeito financeiro não fica com o modelo.
- **Só promoção ativa no sistema.** Campanha prevista no manual (Black Friday, Semana do Músico)
  não é prometida antes de existir no sistema.
- **Verificação do pedido por número e contato do titular.** Recusado: só o número (revela pedido
  alheio a quem tentar números em sequência). A base não tem dado mais forte (CPF).
- **O cliente vê "disponível" ou "indisponível", não a quantidade em estoque.** Evita prometer
  unidades que podem não existir (há status contraditórios na base).
- **Repositório público `artefact-challenge`** (resposta à Q-01, dono, 2026-11-02: "o nome do repo
  é: artefact-challenge"). A criação do repositório público é confirmada com o dono uma vez, na
  T-09; depois, push ao fim de cada fase.
- **Cota do plano gratuito usada com parcimônia** (resposta à Q-02, dono, 2026-11-02: "nao vai
  acabar, só não abusar"). Avaliação completa só depois de mudança que possa afetá-la; caso
  isolado se repete sozinho. Se ainda assim a cota acabar, vale P-07 (outro modelo gratuito).

## 6. Fora de escopo

| Item | Por quê | Para onde vai |
|---|---|---|
| Integração com WhatsApp | O enunciado aceita linha de comando; o foco é o agente | README, "o que faria com mais tempo" |
| Interface web ou API | Idem | README, idem |
| Persistência da conversa entre sessões | Decisão da §5 | README, idem |
| Rastreamento real nos Correios ou na Jadlog | Os códigos são fictícios e não há integração | A assistente informa o código e onde consultar (§5.3) |
| Cálculo de frete por CEP | O manual o condiciona a CEP, peso e dimensões, que a base não tem | A assistente explica a regra e encaminha |
| Executar troca, devolução ou cancelamento | Decisão da §5 | Encaminhamento (R-11) |
| Busca tolerante a erro de digitação | O modelo costuma corrigir o termo antes de consultar; custo alto para o prazo | README, limitações conhecidas |
| Corrigir as tabelas da loja (descrições trocadas, totais divergentes, status contraditórios) | São dados da loja: o agente lê, não corrige (R-17) | README, inconsistências reportadas à loja |
| Avaliação de tom por outro modelo (juiz) | Prazo; o tom é conferido pelo dono (CA-16) | README, o que faria com mais tempo |
| Feriados no horário de funcionamento | O manual não lista os feriados | README, limitações conhecidas |

## 7. Consequências e riscos aceitos

- **Plano gratuito do Gemini:** segundo a página de preços do Google (consultada em 2026-11-02), o
  conteúdo enviado no plano gratuito é usado para melhorar os produtos do Google. Aceitável com
  dados fictícios; em produção, plano pago. O README declara isso.
- **Modelo barato erra mais:** as regras de dinheiro, data e privacidade não dependem dele, e a
  avaliação mede o resto. Se não bastar, P-07.
- **Não determinismo:** a avaliação passa em duas execuções seguidas; isso não garante a mesma
  resposta em toda execução.
- **Limite de uso do plano gratuito** pode atrasar avaliação e exemplos.
- **E-mail compartilhado (clientes 11 e 43):** quem tiver esse e-mail e o número de um pedido do
  cliente 11 verá o pedido. É risco do dado; o telefone é único.
- **Data de recebimento é a prevista (P-02):** a elegibilidade calculada pode diferir da real em
  alguns dias. A assistente diz a data usada e quem decide é a equipe (R-10).

## 8. Premissas assumidas

- **P-01 · Contradições do manual.** Contato oficial: (67) 3341-4444 (capa e §1.2) e
  contato@emporiodamusica.com.br (sem acento, como na capa). Parcelamento pelo §3.1, mais
  específico que a tabela: até 3x, parcela mínima de R$ 50,00; de 4x a 6x, R$ 80,00; de 7x a 12x,
  R$ 100,00; 1x sempre. A base consultada pelo agente é o manual fiel com só essas correções,
  listadas no README como inconsistências reportadas à loja. Se o dono escolher outro contato, só
  a base muda.
- **P-02 · Pedido é compra com entrega.** Todo pedido da base foi feito a distância (há código de
  rastreio e previsão), logo vale o arrependimento do §4.1; a data de recebimento é a data prevista
  de entrega.
- **P-03 · Relógio real no fuso de Campo Grande** (UTC−4, sem horário de verão), com data e hora
  fixáveis por configuração para testes e demonstração.
- **P-04 · Descrição com outra marca não é confiável.** Quando a descrição cita uma marca que não
  está no nome do produto, ela é descartada e a assistente fala só do que nome, preço e
  especificações dizem. As especificações genéricas (spec §1) continuam sendo mostradas como estão.
- **P-05 · Significado dos status de pedido:** pendente = aguardando confirmação do pagamento;
  confirmado = pagamento confirmado, em preparação; enviado; entregue; cancelado (com o motivo
  gravado).
- **P-06 · A persona não tem nome próprio:** "assistente virtual da Empório da Música".
- **P-07 · Escada de modelo.** Se o modelo padrão não passar na avaliação depois de ajustes nas
  instruções e nas descrições das consultas, uso o próximo mais barato com plano gratuito e
  registro os números no LOG. Com a chave gratuita, isso não tem custo para o dono.
- **P-08 · Frete de exatamente R$ 500,00 não é decidido pela assistente.** O manual não cobre
  esse valor; ela diz isso e oferece encaminhar (R-09).

## 9. Questões em aberto

Nenhuma. Q-01 e Q-02 foram respondidas em 2026-11-02 e viraram decisões na §5.

## Referências

- Enunciado do desafio e dados originais: pasta local `Desafio Técnico AI Engineer 2026/`, fora do
  controle de versão.
- Manual de Políticas e Procedimentos da Empório da Música, versão 2.1 (junho de 2025).
- Google AI Studio, páginas de preços e de modelos, consultadas em 2026-11-02:
  https://aistudio.google.com/docs/pricing e https://aistudio.google.com/docs/models
