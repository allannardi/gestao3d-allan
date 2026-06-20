# Gestão 3D Allan v07.07 - CSS Pedidos Mobile chamado corretamente

Correção aplicada:

- A função `pedidos_resumo_mobile_css()` existia, mas não estava sendo chamada na página Pedidos.
- Por isso o resumo mobile aparecia como texto simples.
- Agora a página chama:
  - `pedidos_mobile_css()`
  - `pedidos_resumo_mobile_css()`
- Também ajustado o título principal `h1` para usar azul escuro da paleta:
  `#0A1A5C`

Arquivos alterados:
- `pages/5_Pedidos.py`
- `components/mobile_nav.py`

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Abrir Pedidos no celular/tela estreita
3. Confirmar o card em degradê no topo
4. Confirmar os KPIs em cards
5. Confirmar o título em azul escuro
