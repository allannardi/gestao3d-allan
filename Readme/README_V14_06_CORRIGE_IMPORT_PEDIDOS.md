# V14.06 — Correção do import da listagem de pedidos

## Objetivo
Corrigir o erro ao abrir a tela Pedidos:

`ImportError: cannot import name 'carregar_pedidos_listagem_cache' from 'services.pedidos'`

## Alterações
- Garantido que `services/pedidos.py` possui a função `carregar_pedidos_listagem_cache()`.
- Adicionado fallback de segurança em `pages/5_Pedidos.py`.
- Sidebar renumerada para `0.14.06`.

## O que não mudou
- Visual.
- Banco de dados.
- Regras de negócio.
- Cálculos.
- Status.
- Fluxo de pedidos.

## Observação
Se o sidebar ainda aparecer como versão antiga depois de copiar os arquivos, reinicie o Streamlit e atualize a página com Ctrl+F5.
