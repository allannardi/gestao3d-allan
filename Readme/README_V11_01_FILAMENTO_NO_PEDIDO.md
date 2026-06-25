# Gestão 3D Allan v11.01 - Filamento real no pedido

Objetivo:
Alterar o fluxo para que a peça tenha apenas uma referência de filamento para cálculo previsto,
mas a confirmação do filamento/cor real aconteça no pedido.

## Peças
- Os filamentos cadastrados na peça passam a ser tratados como referência de cálculo.
- A cor real usada na venda não fica mais presa à peça.
- Textos da tela de Peças foram ajustados para deixar isso claro.

## Pedidos
- No Novo Pedido foi adicionada a etapa "Filamento real".
- Após escolher peça e quantidade, o sistema mostra:
  - uso/referência do filamento;
  - gramas necessárias para o pedido;
  - filamentos ativos disponíveis;
  - saldo estimado disponível em gramas;
  - saldo estimado após o pedido.

## Disponibilidade
- Foi adicionada a coluna `peso_g` em `pedido_filamentos`.
- A disponibilidade é calculada assim:
  - peso original do rolo;
  - menos gramas já confirmadas em pedidos não cancelados.

## Edição de pedido
- O modal de edição também permite revisar o filamento real usado.
- Ao editar, o pedido atual não é descontado duas vezes da disponibilidade.

## Duplicação de pedido
- Ao duplicar um pedido, os filamentos reais selecionados também são copiados.

## Filamentos
- Resultados do filamento passam a considerar os pedidos onde o filamento foi realmente usado.
- Isso substitui a lógica antiga baseada apenas na referência cadastrada na peça.

Migração segura:
- Adiciona `peso_g` na tabela `pedido_filamentos`.
- Não apaga dados.
- Não recria tabelas.
- Não remove cadastros existentes.

Observação:
- Pedidos antigos que não tinham filamento real/gramas preenchidos não terão consumo retroativo automaticamente.
- A partir desta versão, os novos pedidos passam a registrar o consumo estimado por filamento.
