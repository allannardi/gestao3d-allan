# Gestão 3D Allan v07.17 - Correção moeda em Clientes

Correção aplicada:

- A aba Clientes passou a mostrar resultados financeiros por cliente.
- A função `moeda()` era usada nesses resultados, mas ainda não existia em `pages/4_Clientes.py`.
- Foi adicionada a função `moeda(valor)` na página Clientes.
- Filamentos foi preservado, pois já estava funcionando.

Nenhuma regra de cálculo foi alterada.
Nenhuma estrutura de banco foi alterada.
Arquivos Python validados por compilação antes de gerar o ZIP.

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Abrir Clientes
3. Abrir Detalhes e ações de um cliente
4. Confirmar se aparecem faturamento, lucro, ticket médio e pedidos vinculados
5. Abrir Filamentos e confirmar que continua funcionando
