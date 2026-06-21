# Gestão 3D Allan v08.13 - Fix cor dos botões Salvar

Objetivo:
Ajustar a cor do texto dos botões principais de ação/salvamento, principalmente os botões "Salvar" que estavam com contraste insuficiente.

Alterações:
- Botões de `st.form_submit_button` agora ficam com:
  - fundo em degradê azul do projeto;
  - texto branco;
  - hover consistente;
  - ícones/textos internos forçados em branco.
- Reforço de cor branca para CTAs principais (`kind="primary"`).

Preservado:
- Mobile aprovado;
- Layout desktop;
- Sidebar;
- Cards;
- Tabelas;
- Regras de negócio.

Teste rápido:
1. Rodar `streamlit run Dashboard.py`;
2. Validar os botões:
   - Salvar Peça;
   - Salvar Filamento;
   - Salvar Cliente;
   - Salvar Acessório;
   - Salvar Configurações;
   - Salvar Alterações (edições).
