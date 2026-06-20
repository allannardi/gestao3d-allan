# Gestão 3D Allan v08.01 - Desktop visual base

Objetivo:

Trazer o visual do desktop para mais perto do padrão aprovado no mobile, sem mexer em regras de negócio.

Alterações aplicadas:

- Criado o componente `components/desktop_visual.py`.
- Títulos principais (`h1`) em azul escuro da paleta: `#0A1A5C`.
- Sidebar com visual mais premium:
  - fundo branco;
  - item ativo em azul claro;
  - textos com peso e cor mais alinhados ao projeto;
  - hover mais suave.
- Botões com visual mais profissional:
  - primário em degradê azul;
  - secundário branco com borda azul clara;
  - hover mais elegante.
- Containers nativos com:
  - bordas mais arredondadas;
  - sombra suave;
  - aparência menos padrão Streamlit.
- Inputs, selects e textareas com bordas mais suaves.
- Expanders com visual mais limpo.
- DataFrames/tabelas com borda e sombra mais refinadas.

Preservado:

- Mobile atual.
- Cálculos.
- Banco de dados.
- Navegação.
- Layout funcional das páginas.

Arquivos alterados:

- `components/desktop_visual.py`
- `Dashboard.py`
- `pages/1_Filamentos.py`
- `pages/2_Acessorios.py`
- `pages/3_Pecas.py`
- `pages/4_Clientes.py`
- `pages/5_Pedidos.py`
- `pages/Configuracoes.py`
- `pages/6_Mais.py`

Teste:

1. Rodar `streamlit run Dashboard.py`.
2. Validar visual no desktop:
   - Dashboard
   - Pedidos
   - Peças
   - Clientes
   - Mais
3. Validar rapidamente no mobile para confirmar que nada foi afetado.
