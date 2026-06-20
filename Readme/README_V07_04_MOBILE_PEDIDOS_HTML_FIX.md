# Gestão 3D Allan v07.04 - Correção HTML Pedidos Mobile

Correção aplicada:

- Alguns blocos HTML dos cards de pedidos estavam aparecendo como texto/código na tela.
- A renderização dos cards de pedidos foi alterada para `st.html(html)`, com fallback para `st.markdown`.
- Nenhuma regra de cálculo foi alterada.
- Nenhuma lógica de banco foi alterada.
- Layout desktop preservado.

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Abrir a página Pedidos no modo celular
3. Confirmar que não aparecem mais textos como `<div class=...>`
4. Validar os cards de pedidos, detalhes e botões.
