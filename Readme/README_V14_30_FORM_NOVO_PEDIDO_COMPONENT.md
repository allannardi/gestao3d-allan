# V14.30 — Formulário de Novo Pedido em componente

## Objetivo
Continuar a organização da tela Pedidos, separando o formulário de novo pedido da página principal.

## O que foi criado
- `components/pedido_novo_form.py`

## O que foi movido
Saiu de `pages/5_Pedidos.py` o bloco do formulário acionado pelo botão `+ Novo Pedido`.

Esse fluxo agora fica em:

- `components/pedido_novo_form.py`

## O que permanece na página Pedidos
A página continua responsável por:
- carregar dados principais;
- mostrar resumo;
- abrir ou fechar o formulário;
- listar pedidos cadastrados;
- editar, duplicar e alterar status.

## O que não mudou
- Visual.
- Banco de dados.
- Criação de pedido.
- Cadastro rápido de cliente dentro do pedido.
- Seleção de peça.
- Seleção de impressora.
- Seleção de filamento/rolo.
- Cálculo de preço, lucro e lucro/hora.
- Alertas antes de salvar.
- Regras de cálculo.

## Validação recomendada
- Abrir a tela Pedidos.
- Clicar em `+ Novo Pedido`.
- Criar pedido com cliente existente.
- Criar pedido com novo cliente rápido.
- Selecionar peça, impressora e filamento.
- Alterar preço, desconto e frete.
- Conferir resumo do pedido.
- Salvar pedido.
- Conferir se o pedido aparece na lista.
