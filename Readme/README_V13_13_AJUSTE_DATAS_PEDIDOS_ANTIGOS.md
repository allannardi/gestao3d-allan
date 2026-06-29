# V13.13 — Ajuste pontual de datas dos pedidos antigos

## Objetivo
Evitar ajuste manual das novas datas nos pedidos já cadastrados.

## Onde fica
Configurações > Impressoras > Ajuste pontual de datas dos pedidos antigos

## O que a ação faz
Para pedidos antigos que possuem Entrega Prevista, o sistema preenche:

- Data Final Produção = Entrega Prevista
- Data da Entrega = Entrega Prevista

## Segurança
- A ação exige confirmação por checkbox.
- Só preenche datas vazias.
- Não sobrescreve datas já preenchidas manualmente.
- Não altera status.
- Não altera preço, cliente, peça, filamento ou impressora.
- É uma ação pontual para regularizar histórico.

## Impacto no Dashboard
Depois do ajuste, o gráfico de utilização por mês passa a distribuir os pedidos antigos pela Data Final Produção preenchida.
