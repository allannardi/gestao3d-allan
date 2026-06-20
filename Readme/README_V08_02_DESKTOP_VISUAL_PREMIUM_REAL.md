# Gestão 3D Allan v08.02 - Desktop visual premium real

Objetivo:

Deixar o desktop visualmente mais próximo do mobile aprovado, sem alterar o mobile.

Alterações aplicadas:

## Sidebar
- `components/sidebar.py` redesenhado.
- Logo com card/sombra.
- Nome Gestão 3D em azul escuro.
- Separadores mais elegantes.
- Itens com hover e item ativo mais destacados.
- Versão no rodapé mais discreta.

## Dashboard desktop
- Adicionado card hero em degradê no topo da Dashboard desktop:
  - resumo executivo;
  - faturamento do mês;
  - pedidos fechados;
  - indicadores rápidos.
- Mantidos os KPIs existentes abaixo.

## Tabelas da Dashboard
- Tabelas da Dashboard redesenhadas:
  - bordas mais arredondadas;
  - sombra;
  - cabeçalho em azul escuro;
  - status em chip visual;
  - linhas com hover mais elegante.

## Preservado
- Mobile aprovado preservado.
- Cálculos preservados.
- Banco preservado.
- Navegação preservada.

Arquivos alterados:
- `components/sidebar.py`
- `components/desktop_visual.py`
- `components/desktop_hero.py`
- `Dashboard.py`

Teste:
1. Rodar `streamlit run Dashboard.py`.
2. Validar desktop:
   - sidebar;
   - Dashboard;
   - tabelas da Dashboard;
   - Pedidos.
3. Validar rapidamente mobile para confirmar que não mudou.
