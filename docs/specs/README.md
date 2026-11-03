# Specs — desenvolvimento guiado por especificação

Toda mudança relevante deste projeto ganha uma pasta aqui, escrita **antes** do código.
Este arquivo é a convenção e o índice. Vale para pessoas e para qualquer agente, de qualquer
ferramenta: as regras estão aqui, não na memória de uma conversa.

---

## Quando escrever uma spec

O critério é o custo de errar, não o tamanho do diff.

| Escreva spec | Vá direto ao código |
|---|---|
| Toca segurança, dinheiro, dados do usuário ou permissão | Texto, cor, espaçamento |
| Muda contrato de API, schema, formato de arquivo ou evento | Renomear, extrair função sem mudar comportamento |
| Mexe em cálculo, regra de negócio ou dado existente | Typo, link quebrado |
| Envolve 3+ arquivos, ou as duas pontas (cliente e servidor) | Bug de uma linha com causa óbvia |
| Tem decisão que alguém vai questionar daqui a três meses | Atualização de dependência sem quebra |
| Pode regredir em silêncio | Qualquer mudança cujo diff cabe numa frase |

**Na dúvida:** se você precisaria explicar a decisão para outra pessoa daqui a três meses,
escreva a spec.

## Tamanhos

| Tamanho | Quando | Arquivos |
|---|---|---|
| **S** | Correção localizada (causa única, até 3 arquivos de código de produção, sem decisão de desenho), inclusive em área sensível, que precisa de registro | `spec.md` único (modelo lite), até umas 120 linhas |
| **M** | Feature; correção com decisão de desenho; mudança de contrato, schema, regra de cálculo ou permissão; 4+ arquivos de código de produção; as duas pontas | `spec.md` · `design.md` · `tasks.md` · `STATUS.md` · `LOG.md` |
| **L** | M com fases entregáveis separadas, migração de dados, várias sessões ou agentes | como M, com fases no design e no tasks |

Testes e documentação não contam como arquivos. "Decisão de desenho" é uma escolha que alguém de
fora da tarefa questionaria porque afeta contrato, dado gravado, outros módulos ou comportamento
visível; escolha local de implementação não é. Fazer o código cumprir uma regra que o projeto já
documenta é correção. Uma spec S que cresce (decisão de desenho, contrato, schema, mais áreas) é promovida a M
antes de continuar.

## Estrutura

```
NNN-nome-em-kebab-case/
├── STATUS.md   estado ATUAL. Reescrito no lugar. Primeiro arquivo a ler.
├── spec.md     o QUÊ e o PORQUÊ: problema, requisitos, critérios de aceite, fora de escopo.
├── design.md   o COMO: ponto de partida conferido, decisões, contratos, arquivos, riscos.
├── tasks.md    passos atômicos e ordenados, cada um com verificação própria.
├── LOG.md      diário, só se acrescenta. O que aconteceu, o que se aprendeu.
└── evidence/   (opcional) capturas e saídas que provam critérios. Nunca com dado real de pessoa.
```

Cada arquivo tem um ritmo: `spec.md` quase não muda; `design.md` muda com o aprendizado, mas
sempre descreve a decisão vigente; `tasks.md` é marcado durante a execução; `STATUS.md` é
reescrito a cada sessão; `LOG.md` só cresce. Juntar dois deles num só mistura ritmos e é o que
faz documento de estado virar histórico que ninguém consegue ler.

Spec de tamanho S é um `spec.md` só, com as mesmas partes em seções curtas; o ponto de entrada
dela é a seção "Estado atual".

**Não há CLAUDE.md, AGENTS.md ou arquivo de instrução por spec.** O ponto de entrada de uma
spec é o `STATUS.md`, que qualquer ferramenta lê. Regra que vale para todas as specs mora
aqui; regra que vale para o projeto mora no guia do projeto.

## Numeração e identificadores

- Pastas numeradas em sequência (`001`, `002`…), na ordem de criação, nunca reaproveitadas.
  Spec abandonada fica, com estado `descartada` e o motivo: saber o que foi descartado vale
  mais que uma pasta limpa.
- Identificadores dentro da spec: **R-01** requisito · **CA-01** critério de aceite ·
  **P-01** premissa assumida · **Q-01** questão em aberto · **D-01** decisão · **RS-01** risco · **T-01** tarefa ·
  **A-01** achado registrado. Nunca se renumera; item que sai é marcado como removido.
- Fora da própria pasta, cite com o número da spec: `012/D-03`.

## Estados de uma spec

| Estado | Significa |
|---|---|
| `rascunho` | Em escrita. Questões em aberto permitidas. |
| `aprovada` | O dono aprovou; nenhuma questão bloqueante; revisão de consistência feita. |
| `em execução` | Há tarefas em andamento. |
| `implementada` | Código e verificações automatizadas prontos; aceite manual ou em ambiente real pendente, com os CA nomeados. |
| `concluída` | Todos os CA verificados e documentação fechada. |
| `concluída com ressalvas` | O que faltou foi movido para um lugar rastreado (roadmap, issue), com dono. Nada fica pendente só dentro da spec. |
| `pausada` · `descartada` · `substituída por NNN` | Com o motivo, sempre. |

Uma spec não fica `implementada` indefinidamente: no fechamento, o aceite pendente é feito ou
movido para fora com dono, e a spec conclui com ressalvas. Voltar um passo é normal (uma rodada de
revisão reabre `implementada` para `em execução`), com o motivo no LOG.

**Aprovação.** Quando o dono pede a mudança em si ("corrija isso") e nenhuma questão bloqueante
muda o que será feito, o pedido é a aprovação do escopo: a spec vai de `rascunho` a `em execução`,
com as palavras dele no LOG. Quando o pedido era especificar, a spec espera a aprovação explícita.

## O fluxo

```
investigar → spec.md → design.md → tasks.md → revisão → aprovação → executar → fechar
```

Cada etapa é uma chance barata de descobrir que a anterior estava errada. Revisar um
`design.md` custa minutos; refazer a implementação custa horas. Nunca pule da spec para o código.

## Regras

1. **Investigue antes de especificar.** Leia inteiro o código envolvido e confira o diagnóstico
   existente: ele costuma subestimar o problema. Premissa que não deu para conferir vira tarefa
   da Fase 0, antes de qualquer código.
2. **`spec.md` não fala de implementação.** Arquivo, função, biblioteca, tabela: isso é design.
   Em spec S, só a seção "Correção" fala.
3. **Todo critério de aceite é verificável e diz como.** Ao menos um é automatizado. Todo
   requisito é coberto por algum critério.
4. **Fora de escopo é parte da spec**, com o motivo e o destino de cada item. É o que impede a
   spec de crescer sozinha durante a execução.
5. **Tarefa é atômica:** um objetivo, os arquivos, uma verificação. Se não dá para marcar como
   feita sem ressalva, está grande demais. `[x]` só com a verificação executada.
6. **Toda spec nasce com teste.** A tarefa de teste vem antes da implementação, e o vermelho
   pelo motivo esperado é visto e registrado. Teste que não pode falhar não é teste.
7. **Defeito achado no caminho vira registro, não correção.** Vai para os achados do STATUS e
   para o registro permanente do projeto (seção "Limitações conhecidas" do
   [README](../../README.md) da raiz, com data); vira spec própria. Corrigir comportamento no meio de
   outra mudança torna as duas inverificáveis. Exceção declarada: ajuste sem mudança de
   comportamento observável.
8. **Decisão contrariada vira registro.** Se a execução fez diferente do design, o `design.md`
   é atualizado (decisão antiga marcada como substituída) e o LOG conta o porquê. Spec que
   mente é pior que spec nenhuma.
9. **`STATUS.md` é atualizado durante o trabalho, não no fim**, e reescrito no lugar. O valor
   dele é sobreviver a uma interrupção de duas semanas ou a uma troca de agente.
10. **Afirmação sobre sistema real se confere no sistema real.** Migration prova o que foi
    escrito, não o que foi aplicado; rota documentada não prova rota alcançável. Consulte o
    banco, exercite a rota, inspecione o build.
11. **Diga o nível da evidência:** implementado, testado, validado em ambiente real, aceito pelo
    dono. Nunca chame um pelo nome do outro, e diga o que a evidência não prova.
12. **Número que muda de propósito é calculado antes**, à mão ou por script, e escrito na spec.
    A suíte fica vermelha contra o valor antigo só nos campos esperados, e só então o código
    muda. Nunca se regenera uma referência para calar um teste.
13. **Passo irreversível é marcado ⛔** e só roda com a pré-condição conferida. (⚠️ é aviso comum:
    "cuidado aqui"; ⛔ é "isto não tem volta".)
14. **A última tarefa é o fechamento da documentação**, pelo checklist do projeto, com as
    contagens conferidas por comando como último passo.

## Verificação mecânica

Se o verificador estiver instalado nesta pasta, rode antes de pedir aprovação e ao fechar:

```bash
python3 docs/specs/check_spec.py docs/specs/NNN-nome      # uma spec
python3 docs/specs/check_spec.py --all docs/specs         # todas, mais o índice
```

Ele confere o que é contável (rastreabilidade, marcadores esquecidos, estado incoerente, STATUS
empilhado). Passar nele não quer dizer que a spec está boa: a leitura crítica por alguém que não
a escreveu continua obrigatória em spec M ou L.

## Revisões do dono do projeto

Quando o dono revisa o resultado (prints, uso real) e pede ajustes:

- a rodada entra no `tasks.md` como nova fase ("Revisão de AAAA-MM-DD"), com tarefas numeradas
  em sequência e verificação própria;
- o que muda requisito é editado no `spec.md` no lugar, com "(revisado em AAAA-MM-DD)";
- o que muda decisão atualiza a D-NN no `design.md`;
- o pedido, com as palavras do dono quando decidem algo, vai para o LOG;
- preferência que vale além desta spec vai para o documento permanente do projeto;
- pedido que é capacidade nova vira spec nova.

## Ligação com o resto do projeto

- A spec **cita** achados, issues e itens de roadmap que resolve; não os copia.
- Terminada a spec, os documentos permanentes são atualizados pelo checklist de fechamento e
  o item do roadmap recebe a marca de concluído com data.
- **A spec é o registro da decisão; os documentos permanentes são o estado atual do sistema.**
  Depois de concluída, a spec explica como chegamos aqui; a fonte da verdade é o código e a
  documentação permanente.
- Commits referenciam a spec, de preferência um por fase:

```
feat(escopo): descrição curta

refs docs/specs/NNN-nome/spec.md
```

---

## Índice

| # | Spec | Tamanho | Estado | Resolve |
|---|---|---|---|---|
| [001](001-agente-de-atendimento/STATUS.md) | Agente de atendimento | L | implementada | — |
