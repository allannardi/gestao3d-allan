# V14.11 — Otimização de cálculo dos pedidos visíveis

## Objetivo
Iniciar a otimização real da tela Pedidos, reduzindo cálculos desnecessários durante o carregamento.

## Alteração principal
Antes:
- a tela carregava os pedidos;
- aplicava filtros;
- calculava custos de todos os pedidos filtrados;
- só depois paginava.

Agora:
- a tela carrega os pedidos;
- aplica filtros;
- pagina;
- calcula custos apenas dos pedidos visíveis na página atual.

## Impacto esperado
A tela Pedidos deve ficar mais leve, principalmente quando houver muitos pedidos cadastrados.

## O que não mudou
- Visual.
- Banco de dados.
- Filtros.
- Paginação.
- Cards.
- Cadastro, edição e duplicação.
- Cálculos exibidos nos pedidos visíveis.
- Regras de negócio.

## Observação
Esta é uma otimização segura e incremental. A próxima etapa pode reduzir também a quantidade de dados carregados do banco.
