# V13.06 — Impressora no Pedido

## Objetivo
Integrar a gestão de impressoras ao fluxo de pedidos.

## Alterações
- Adicionada coluna `impressora_id` na tabela `pedidos`.
- Novo Pedido agora exige/permite escolher a impressora usada.
- O custo sugerido do Novo Pedido passa a usar:
  - energia/hora da impressora escolhida;
  - depreciação/hora da impressora escolhida.
- A edição de pedido permite alterar a impressora.
- A duplicação de pedido preserva a impressora original.
- Na lista de pedidos, os detalhes mostram a impressora usada.
- Na listagem, o cálculo do pedido considera a impressora vinculada quando ela existir.

## Compatibilidade
- Pedidos antigos sem impressora continuam funcionando.
- Quando um pedido antigo não tem impressora, o sistema usa a configuração padrão atual.

## Segurança
- Não apaga dados.
- Não altera pedidos antigos automaticamente.
- Não altera peças, filamentos ou clientes.
