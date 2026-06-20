# Gestão 3D Allan v07.02 - Correção HTML Dashboard Mobile

Correção aplicada:

- Alguns blocos HTML da Dashboard mobile estavam aparecendo como texto/código na tela.
- A causa era a renderização via `st.markdown`, que pode interpretar HTML indentado como bloco de código.
- A renderização da Dashboard mobile foi alterada para `st.html(html)`, com fallback para `st.markdown`.
- Nenhuma regra de cálculo foi alterada.
- Nenhuma lógica de banco foi alterada.
- Menu mobile aprovado foi preservado.

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Abrir a Dashboard em tela estreita/celular
3. Confirmar que não aparecem mais textos como `<div class=...>`
4. Validar os cards:
   - Resumo do mês
   - KPIs
   - Pedidos abertos
   - Peças mais vendidas
   - Status dos pedidos
