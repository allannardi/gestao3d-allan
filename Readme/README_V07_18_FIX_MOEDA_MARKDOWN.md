# Gestão 3D Allan v07.18 - Correção de moeda nas listas

Correção aplicada:

- Em listas com `st.write`, o texto `R$` podia ser interpretado como Markdown/LaTeX.
- Isso fazia aparecer `R22,30` em vez de `R$ 22,30`.
- Foi criada a função `moeda_md()` nas páginas afetadas, escapando o `$` somente nas listas.
- Corrigido em:
  - Clientes > Pedidos deste cliente
  - Filamentos > Pedidos vinculados ao filamento

Nenhuma regra de cálculo foi alterada.
Nenhuma estrutura de banco foi alterada.
Arquivos Python validados por compilação antes de gerar o ZIP.

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Abrir Clientes > Detalhes e ações
3. Conferir se aparece R$ corretamente nos pedidos do cliente
4. Abrir Filamentos > Detalhes, peças vinculadas e ações
5. Conferir se aparece R$ corretamente nos pedidos vinculados
