# Gestão 3D Allan v09.02 - Lazy loading de detalhes

Objetivo:
Reduzir recarregamentos pesados causados pelo comportamento padrão do Streamlit.

Contexto:
No Streamlit, a página é executada novamente a cada clique/interação.
Além disso, conteúdo dentro de `st.expander` também é processado mesmo quando o expander está fechado.
Por isso, detalhes pesados dentro de várias listas podem deixar a tela lenta.

Alterações aplicadas:

## Clientes
- Resultados do cliente deixam de ser calculados automaticamente para todos os clientes.
- Agora aparecem somente após clicar em "Carregar resultados do cliente".

## Filamentos
- Peças vinculadas e resultados do filamento deixam de ser carregados automaticamente para todos os filamentos.
- Agora aparecem somente após clicar em "Carregar peças e resultados".

## Peças
- Pedidos desta peça deixam de ser carregados automaticamente para todas as peças.
- Agora aparecem somente após clicar em "Carregar pedidos desta peça".

Preservado:
- Visual aprovado.
- Mobile aprovado.
- Desktop aprovado.
- Cálculos.
- Banco de dados.
- Regras de negócio.

Impacto esperado:
- Telas de Clientes, Filamentos e Peças devem abrir com menos consultas ao banco.
- A diferença fica maior conforme o número de cadastros e pedidos cresce.
- O usuário ainda consegue ver todos os detalhes, mas sob demanda.

Teste:
1. Rodar `streamlit run Dashboard.py`.
2. Abrir:
   - Clientes;
   - Filamentos;
   - Peças.
3. Confirmar que a página abre normalmente.
4. Abrir "Detalhes e ações".
5. Clicar nos botões de carregar resultados/pedidos.
6. Confirmar que os resultados aparecem corretamente.
