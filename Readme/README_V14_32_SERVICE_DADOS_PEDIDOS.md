# V14.32 — Service de dados auxiliares da tela Pedidos

## Objetivo
Continuar a limpeza final da tela Pedidos antes do checkpoint seguro e da futura etapa de usuários.

## O que foi criado
- `services/pedido_dados.py`

## O que foi movido
Saíram de `pages/5_Pedidos.py` e foram para `services/pedido_dados.py`:
- garantia estrutural de tabelas usadas por Pedidos;
- geração de código de cliente rápido;
- carregamento das configurações usadas na tela Pedidos.

## Ajuste adicional
O dialog de duplicação também passou a reutilizar a função centralizada de geração de código de cliente.

## O que não mudou
- Visual.
- Banco de dados.
- Criação de pedido.
- Edição de pedido.
- Duplicação de pedido.
- Alteração de status.
- Filamentos do pedido.
- Filtros.
- Paginação.
- Regras de cálculo.

## Validação recomendada
- Abrir a tela Pedidos.
- Clicar em `+ Novo Pedido`.
- Criar pedido com cliente existente.
- Criar pedido com novo cliente rápido.
- Duplicar um pedido cadastrando novo cliente.
- Editar um pedido.
- Alterar status.
- Excluir um pedido de teste, se necessário.
