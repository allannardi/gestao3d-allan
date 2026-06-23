# Gestão 3D Allan v10.04 - Correção formato de datas nos inputs

Correção:
- Ajustado o formato visual dos campos de data do Streamlit para `DD/MM/AAAA`.

Locais corrigidos:
- Novo Pedido:
  - Data do pedido;
  - Entrega prevista.
- Novo Filamento:
  - Data da compra.

Causa:
- As datas exibidas em textos/listagens já estavam formatadas.
- Porém os campos `st.date_input` ainda estavam usando o formato padrão do Streamlit, aparecendo como `AAAA/MM/DD`.

Preservado:
- Dados existentes.
- Banco de dados.
- Cálculos.
- Pós-processamento.
- Paginação.
- Visual aprovado.
- Mobile aprovado.
