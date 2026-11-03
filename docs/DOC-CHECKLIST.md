# Fechamento de documentação

**Quando rodar:** ao concluir uma spec (é a última tarefa de todo `tasks.md`), ao fim de cada
fase de uma spec grande, e antes do commit que fecha qualquer correção grande. Não é opcional
e não espera pedido.

**Por que existe:** nenhum documento é verificado por teste, então todos divergem do código em
silêncio. O teste fica vermelho; o documento continua bonito e mentindo. E quem lê um
documento desatualizado não tem uma informação imprecisa: toma uma decisão errada com
confiança.

---

## 1. O que mudou → o que conferir

<!-- Adapte ao projeto: uma linha por documento permanente que existe aqui. -->

| Mudou | Confira |
|---|---|
| Ferramenta do agente: nome, parâmetro, formato de retorno | README (decisões técnicas) e a persona (`src/emporio/persona.md`) |
| Estrutura de pastas, dependência, ordem de inicialização | README (como rodar, arquitetura) e AGENTS.md |
| Regra de preço, parcelamento, disponibilidade, verificação de pedido | README (decisões técnicas) |
| Manual curado (`data/politicas_da_loja.md`) | o preâmbulo de correções do próprio arquivo e o README (tratamento dos dados) |
| Caso de avaliação, modelo padrão | README (avaliação, com o resultado medido) e `.env.example` |
| Achado corrigido, agravado ou descoberto | README, "Limitações conhecidas" — registre a data, não apague |
| Item de "o que faria com mais tempo" feito ou descartado | README, mesma seção |
| Variável de ambiente, passo de instalação | README (como rodar) e `.env.example` |
| Conversa de exemplo regenerada | `examples/` e as citações no README |
| Comando, convenção, proibição | guia do projeto para agentes (CLAUDE.md / AGENTS.md) |
| Contagem de teste, estágio do produto, stack | README da raiz: é o primeiro arquivo que alguém de fora lê |
| Qualquer uma das anteriores | o `STATUS.md` da spec e o índice de specs |

## 2. As armadilhas recorrentes

Na ordem em que costumam envelhecer:

1. **Data do cabeçalho.** "Atualizado em" mentindo é pior que ausente: autoriza o leitor a
   confiar no resto.
2. **Contagem velha.** Teste, tela, rota, arquivo, linha. Confira por comando, nunca de memória,
   e nunca copie a contagem de outro documento: contagem herdada não é contagem conferida.
3. **Contagem escrita no meio da sessão.** O número estava certo quando foi escrito e envelheceu
   antes do commit, porque a revisão seguinte acrescentou arquivos. Rode os comandos da §3 como
   **último passo antes do commit**.
4. **Afirmação de segurança obsoleta.** Documento que descreve buraco já fechado, ou fechado um
   que continua aberto. É a pior de envelhecer, porque descreve um sistema que não existe.
5. **Item de roadmap concluído sem marca.** O próximo planejamento o conta de novo.
6. **Seção grudada no fim.** Spec nova costuma apendar "## Título (spec NNN)" no rodapé de um
   documento. No fechamento, o conteúdo vai para a seção que já trata do assunto, e o apêndice
   some.
7. **Texto de sessão em documento permanente.** "Pendente de aceite", "o usuário vai revisar",
   "não usar navegador nesta etapa" são registro de execução: moram no STATUS ou no LOG. O
   documento permanente descreve o sistema, não a conversa.
8. **Guia de instalação e `.example` fora de sincronia.** São o único par que alguém segue ao pé
   da letra, e o único cuja desatualização instala um defeito.
9. **`arquivo:linha` em documento permanente.** A linha envelhece a cada refatoração e um número
   errado faz duvidar do parágrafo inteiro. Prefira o nome da função ou símbolo.

## 3. Contagens por comando

<!-- Adapte: os comandos que produzem os números que os documentos citam. -->

```bash
# testes offline (totais na última linha)
uv run pytest -q

# avaliação com o modelo real (casos e resultado)
uv run pytest evals -q

# exemplos de conversa e seções do manual curado
ls examples/*.md | wc -l
grep -cE '^#{2,3} [0-9]' data/politicas_da_loja.md

# dados da loja iguais aos originais (compare com os hashes do LOG da spec 001)
sha256sum data/*.csv data/politicas_da_loja.pdf

# nada que não deve ir para o git: deve voltar vazio
git -c core.quotePath=false ls-files | grep -E '^(\.env$|var/|\.agents/|Desafio)'
```

O que o comando não dá, o sistema real dá: permissões, políticas, objetos existentes. Confira
afirmação sobre o banco consultando o banco, não relendo o arquivo de migration.

## 4. O teste final

Leia cada documento alterado como quem chega hoje ao projeto e **acredita nele**. Se acreditar
em algo que não é verdade, o custo é de quem leu.

Se um documento discordar do código, o código está certo. Corrija o documento na hora.
**Exceção:** quando a divergência é um defeito já registrado (o documento descreve o comportamento
certo e o código ainda não o cumpre), o documento não passa a descrever o defeito: ganha uma nota
apontando o achado, até a correção.
