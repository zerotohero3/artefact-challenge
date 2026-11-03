# Exemplo 4 — Pedido atrasado e encaminhamento

Modelo `google:gemini-3.5-flash-lite`, executado em 02/11/2026 23:21 (horário de Campo Grande).

**Cliente:** Cadê meu pedido 8?

> (sem consulta)

**Assistente:** Para eu consultar o seu pedido 8, você poderia me informar o e-mail ou o telefone que usou no cadastro da compra?

**Cliente:** Meu e-mail é anacarol.ferreira@coldmail.com

> consulta: `get_order(order_id=8, contact='anacarol.ferreira@coldmail.com')`

**Assistente:** Oi, Ana! Encontrei o seu pedido 8:

- **Status:** Enviado
- **Itens:** 1x Kala KA-C Concert Mogno
- **Total:** R$ 349,90
- **Forma de pagamento:** Cartão de débito
- **Código de rastreio:** `BRJL5544332BR` (você pode acompanhar pelo site dos Correios ou da Jadlog)
- **Previsão de entrega:** 28/02/2026

Como a previsão de entrega era para o dia 28/02/2026, o pedido consta como atrasado. Peço desculpas por isso! Quer que eu encaminhe o seu caso para a nossa equipe verificar o que aconteceu?

**Cliente:** Quero falar com alguém

> consulta: `handoff_to_staff(contact='anacarol.ferreira@coldmail.com', summary='Cliente solicitou atendimento humano para verificar o pedido 8 que está atrasado.', order_id=8, reason='human_request')`

**Assistente:** Ana, registrei seu atendimento sob o protocolo **EM-443263**. 

Como nossa loja está fechada agora, nossa equipe retorna assim que abrir, na terça-feira, 03/11/2026, às 09:00. Eles vão entrar em contato com você pelo e-mail cadastrado. Se precisar de mais alguma coisa até lá, é só falar!
