# Gestão 3D Allan v07.08 - Mobile outras abas

Alterações aplicadas:

- Peças: resumo mobile no mesmo padrão da aba Início/Pedidos.
- Clientes: resumo mobile no mesmo padrão.
- Filamentos: resumo mobile no mesmo padrão.
- Acessórios: resumo mobile no mesmo padrão.
- Configurações: resumo mobile no mesmo padrão.
- Mais: mantém navegação, agora com CSS mobile compartilhado.
- Desktop preservado com os KPIs originais.
- Criado componente genérico `components/mobile_summary.py`.

Padrão visual:
- card principal em degradê;
- KPIs em grade 2x2 no celular;
- títulos em azul escuro da paleta;
- botões principais mais destacados no celular;
- READMEs dentro da pasta `Readme/`.

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Abrir no modo celular:
   - Peças
   - Clientes
   - Mais > Filamentos
   - Mais > Acessórios
   - Mais > Configurações
3. Confirmar que o desktop continua normal.
