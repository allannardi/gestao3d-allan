# Gestão 3D Allan v09.01 - Performance base

Objetivo:
Reduzir tempo de carregamento nas telas mais pesadas sem alterar layout, mobile, cálculos ou regras de negócio.

Principais melhorias:

## Banco local
- Conexão SQLite local configurada com PRAGMAs de performance:
  - WAL;
  - synchronous NORMAL;
  - temp_store MEMORY;
  - cache_size maior.

## Dashboard / Início
- Antes, a Dashboard calculava o custo de cada pedido fazendo consultas repetidas por peça.
- Agora os custos das peças usadas nos pedidos são carregados em lote.
- Isso reduz várias chamadas ao banco, especialmente no Turso/cloud.

## Pedidos
- Resumo dos pedidos otimizado com cálculo de custos em lote.
- Listagem de pedidos otimizada com cálculo de custos em lote.
- A regra de cálculo permanece igual; apenas reduzimos consultas repetidas.

Preservado:
- Mobile aprovado.
- Desktop aprovado.
- Cálculos.
- Banco de dados.
- Regras de negócio.
- Visual.
- Navegação.

Teste recomendado:
1. Rodar `streamlit run Dashboard.py`.
2. Medir sensação de abertura em:
   - Início;
   - Pedidos;
   - abrir/fechar detalhes de pedidos;
   - Novo Pedido.
3. Conferir se totais de faturamento/lucro continuam iguais.
4. Testar online depois do `git push` e reboot do Streamlit Cloud.
