# Gestão 3D Allan v08.03 - Sidebar, tabelas e ranking

Ajustes aplicados conforme validação visual do v08.02:

## Sidebar
- Sidebar ficou mais compacta e limpa.
- Removido uso de margem negativa que gerava visual estranho e barras de rolagem.
- Logo reduzido e melhor encaixado.
- Removido o subtítulo "Portal".
- Grupos e links mantidos no padrão visual do projeto.
- Ajustes aplicados apenas no desktop.

## Tabelas
- Tabelas da Dashboard passam a importar a fonte Barlow dentro do iframe do componente.
- Status continua colorido, mas sem fundo colorido.
- Visual geral mantido mais limpo.

## Ranking de peças
- Ranking deixou de ser por quantidade.
- Agora é ranking por faturamento.
- Substituído gráfico/tabela com cara de Excel por cards com barra horizontal.
- Tooltip/title de cada item contém:
  - faturamento;
  - quantidade;
  - lucro.

Preservado:
- Mobile aprovado.
- Cálculos.
- Banco de dados.
- Navegação.
- Regras de negócio.

Teste:
1. Rodar `streamlit run Dashboard.py`.
2. Conferir sidebar desktop.
3. Conferir Dashboard desktop.
4. Conferir status sem fundo na tabela.
5. Conferir ranking por faturamento.
6. Fazer teste rápido no mobile para confirmar que não mudou.
