# Gestão 3D Allan v07.01 - Mobile Dashboard v02.1

Alterações:

- Dashboard ganhou uma versão específica para celular.
- Desktop continua com o layout atual.
- No celular, a Dashboard mostra:
  - card principal de resumo do mês;
  - KPIs em grade 2x2;
  - pedidos abertos como cards verticais;
  - peças mais vendidas como ranking em cards com barras;
  - status dos pedidos com chips e barras;
  - menos tabelas largas.

Estratégia técnica:

- Foi criada uma área `dashboard_mobile` visível apenas em telas pequenas.
- A área `dashboard_desktop` fica oculta no celular e visível no computador.
- O menu mobile já aprovado foi preservado.

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Abrir no computador: Dashboard deve continuar normal.
3. Reduzir a tela ou abrir no celular: Dashboard deve exibir a versão mobile.
4. Validar se menu inferior continua funcionando.
