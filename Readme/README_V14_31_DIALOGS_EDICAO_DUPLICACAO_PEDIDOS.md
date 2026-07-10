# V14.31 — Dialogs de edição e duplicação de Pedidos

## Objetivo
Continuar a organização interna da tela Pedidos antes da etapa de usuários.

## O que foi criado
- `components/pedido_dialogs.py`

## O que foi movido
Saíram de `pages/5_Pedidos.py` e foram para `components/pedido_dialogs.py`:
- `duplicar_pedido_dialog`
- `editar_pedido_dialog`

## Limpeza adicional
Também foi removida da página uma função antiga de duplicação que não era mais chamada pela interface.

## O que permanece na página Pedidos
A página continua responsável por:
- resumo superior;
- botão `+ Novo Pedido`;
- filtros;
- paginação;
- listagem de pedidos;
- chamada dos dialogs de edição e duplicação.

## O que não mudou
- Visual.
- Banco de dados.
- Edição de pedido.
- Duplicação de pedido.
- Alteração de status.
- Filamentos do pedido.
- Regras de cálculo.
- Filtros.
- Paginação.

## Validação recomendada
- Abrir a tela Pedidos.
- Abrir detalhes de um pedido.
- Clicar em `Editar`.
- Alterar dados e salvar.
- Clicar em `Duplicar`.
- Duplicar para o mesmo cliente.
- Duplicar selecionando outro cliente.
- Duplicar cadastrando novo cliente.
- Alterar status rápido.
