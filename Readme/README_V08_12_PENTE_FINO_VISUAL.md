# Gestão 3D Allan v08.12 - Pente fino visual

Objetivo:
Fazer ajustes finais de consistência visual antes de voltar para performance.

Alterações aplicadas:

## Textos
- Removidas referências antigas ao "Ateliê" nas páginas:
  - Pedidos;
  - Clientes.
- Substituído por "Gestão 3D".

## Desktop
- Ajuste fino de espaçamentos gerais.
- Títulos principais com tamanho mais consistente.
- Subtítulos/captions com melhor leitura.
- Inputs, placeholders, selects e number inputs refinados.
- Botões + e - dos campos numéricos mais alinhados visualmente.
- Expanders com espaçamento e ícones mais consistentes.
- Alerts mais arredondados e com fonte alinhada.
- Radios/checkboxes com fonte mais consistente.
- Modais/dialogs com raio visual mais coerente.
- DataFrames/tabelas com fonte Barlow reforçada.

## Login
- Formulário de login recebeu pequeno refinamento de hover.
- Placeholders e inputs mantêm o novo raio uniforme aprovado.

Preservado:
- Mobile aprovado.
- Cálculos.
- Banco de dados.
- Regras de negócio.
- Dashboard, sidebar, cards, listagens e formulários aprovados.

Teste:
1. Rodar `streamlit run Dashboard.py`.
2. Fazer login.
3. Validar rapidamente:
   - Início;
   - Pedidos;
   - Peças;
   - Clientes;
   - Filamentos;
   - Acessórios;
   - Configurações.
4. Abrir alguns expanders e modais.
5. Fazer teste rápido no mobile.
