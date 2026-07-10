# V14.33 — Correção do filtro de status da tela Pedidos

## Objetivo
Corrigir erro identificado na v14.32 ao abrir a tela Pedidos.

## Erro corrigido
A página ainda usava `STATUS_PEDIDOS` no filtro:

- `["Todos"] + STATUS_PEDIDOS`

Na limpeza da v14.32, esse import foi removido indevidamente da página principal.

## Correção aplicada
- Reincluído o import de `STATUS_PEDIDOS` vindo de `services/pedidos.py`.

## O que não mudou
- Visual.
- Banco de dados.
- Criação de pedido.
- Edição de pedido.
- Duplicação de pedido.
- Alteração de status.
- Filamentos do pedido.
- Filtros, exceto a correção do erro de carregamento.
- Paginação.
- Regras de cálculo.

## Validação recomendada
- Abrir a tela Pedidos.
- Confirmar que o erro não aparece.
- Testar o filtro de status.
- Clicar em `+ Novo Pedido`.
- Abrir/editar/duplicar um pedido existente.
