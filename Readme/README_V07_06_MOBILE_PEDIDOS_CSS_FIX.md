# Gestão 3D Allan v07.06 - Correção CSS Pedidos Mobile

Correções aplicadas:

1. Corrigida a chamada do CSS específico do resumo mobile da página Pedidos.
   Na versão anterior, o topo mobile aparecia como texto simples sem o card em degradê.

2. Títulos principais das páginas agora usam o azul escuro da paleta:
   `#0A1A5C`

Arquivos alterados:
- `pages/5_Pedidos.py`
- `components/mobile_nav.py`

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Abrir a aba Pedidos no modo celular
3. Conferir se o topo ficou com o card em degradê igual ao estilo da aba Início
4. Conferir se o título "Pedidos" está em azul escuro
