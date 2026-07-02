# V14.02 — Início da separação de regras de custos

## Objetivo
Começar a fase de simplificar e separar regras internas, sem mudar telas e sem alterar comportamento do sistema.

## Alterações
- Criada a pasta `services`.
- Criado o arquivo `services/custos.py`.
- Movida para o serviço a regra de cálculo de custo/preço/lucro da tela Peças.
- Criada regra central de resultado de pedido em `services/custos.py`.
- Dashboard e Pedidos passaram a usar a mesma regra central para calcular subtotal, total, custo, lucro, margem e lucro/hora.
- Sidebar renumerada para `0.14.02`.

## O que não mudou
- Banco de dados.
- Estrutura visual das telas.
- Campos.
- Status.
- Datas.
- Regras de negócio.
- Fórmulas de cálculo.

## Por que isso importa
Este é o primeiro passo para deixar o projeto menos pesado de manter.
As telas começam a ficar mais simples, enquanto as fórmulas importantes ficam concentradas em arquivos próprios.
