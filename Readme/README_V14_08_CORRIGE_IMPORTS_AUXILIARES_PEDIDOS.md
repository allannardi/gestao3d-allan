# V14.08 — Correção dos imports auxiliares de Pedidos

## Objetivo
Corrigir o erro ao abrir Pedidos:

`ImportError: cannot import name 'carregar_clientes' from 'services.pedidos'`

## Alterações
- Garantido que `services/pedidos.py` contém:
  - `carregar_clientes()`
  - `carregar_pecas()`
  - `carregar_impressoras_pedidos()`
  - `selecionar_impressora_padrao()`
  - `label_impressora()`
  - `cor_status()`
  - `cor_status_hex()`
- Adicionado fallback de segurança em `pages/5_Pedidos.py`.
- Sidebar renumerada para `0.14.08`.

## O que não mudou
- Visual.
- Banco de dados.
- Regras de negócio.
- Cálculos.
- Fluxo de pedidos.

## Importante
Se a versão antiga continuar aparecendo no sidebar, feche o Streamlit, substitua todos os arquivos do ZIP e abra novamente.
