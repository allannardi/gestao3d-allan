# V14.34 — Listagem de Pedidos em componente

## Objetivo
Finalizar a organização principal da tela Pedidos, separando a listagem visual da página.

## O que foi criado
- `components/pedidos_listagem.py`

## O que foi movido
Saiu de `pages/5_Pedidos.py` o bloco responsável por:
- calcular custos apenas dos pedidos visíveis;
- renderizar os cards de pedidos;
- alterar status rápido;
- mostrar detalhes financeiros;
- mostrar filamentos do pedido;
- chamar editar, duplicar e excluir.

## O que permanece na página Pedidos
A página agora fica mais focada em:
- carregar dados principais;
- exibir resumo superior;
- abrir o formulário de novo pedido;
- aplicar busca;
- aplicar filtro de status;
- paginar os pedidos;
- chamar a listagem visual.

## O que não mudou
- Visual.
- Banco de dados.
- Novo pedido.
- Edição.
- Duplicação.
- Exclusão.
- Alteração de status.
- Filtros.
- Paginação.
- Regras de cálculo.

## Validação recomendada
- Abrir Pedidos sem erro.
- Testar busca.
- Testar filtro de status.
- Trocar página ou quantidade por página.
- Abrir detalhes de um pedido.
- Alterar status rápido.
- Editar pedido.
- Duplicar pedido.
- Excluir um pedido de teste, se necessário.
