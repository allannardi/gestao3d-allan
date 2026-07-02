# V14.04 — Início da separação de regras de pedidos

## Objetivo
Continuar a fase V14 de simplificação interna, começando a tirar regras de pedido da tela `5_Pedidos.py`.

## Alterações
- Criado `services/pedidos.py`.
- Movidos para `services/pedidos.py`:
  - lista oficial de status de pedidos;
  - geração do código do pedido;
  - atualização rápida de status;
  - resumo de prazo entre entrega prevista e entrega real.
- A tela Pedidos continua com o mesmo visual e o mesmo funcionamento.
- Sidebar renumerada para `0.14.04`.

## O que não mudou
- Banco de dados.
- Layout.
- Campos.
- Fluxo de cadastro.
- Fluxo de edição.
- Cálculos.
- Status disponíveis.
- Datas.
- Regras de negócio.

## Por que isso importa
A tela Pedidos é uma das maiores do projeto. Esta versão inicia a separação de regras internas sem mudar o uso do sistema.
