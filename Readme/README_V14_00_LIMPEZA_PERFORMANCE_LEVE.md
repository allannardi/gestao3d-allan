# V14.00 — Limpeza e performance leve

## Objetivo
Abrir a fase V14 com ajustes seguros para reduzir carregamento e simplificar a base, sem mudar regra de negócio.

## Alterações
- Sidebar renumerada para versão 0.14.
- `database.py` renumerado para `v14_00_limpeza_performance_leve`.
- Removida chamada duplicada de `inserir_impressora_padrao()` na inicialização do banco.
- Configurações deixou de usar `inicializar_banco(force=True)` e voltou a usar `inicializar_banco()`, aproveitando o cache de inicialização.
- Removido `import pandas as pd` não utilizado na Dashboard.
- ZIP gerado sem `__pycache__` e sem arquivos `.pyc`.

## O que não foi alterado
- Banco de dados.
- Pedidos.
- Clientes.
- Peças.
- Filamentos.
- Impressoras.
- Cálculo de preço.
- Dashboard e gráficos.
- Regras de status e datas.

## Observação
A ideia desta versão é ser uma limpeza leve e segura. Otimizações mais fortes de Pedidos e Dashboard devem ser feitas em versões separadas.
