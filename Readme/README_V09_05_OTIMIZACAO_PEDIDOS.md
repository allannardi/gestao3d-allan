# Gestão 3D Allan v09.05 - Otimização da página Pedidos

Objetivo:
Reduzir o peso da página Pedidos, uma das telas mais usadas e mais sensíveis ao comportamento do Streamlit.

Problema:
O Streamlit reexecuta a página a cada clique.
Antes, a página Pedidos ainda fazia consultas e cálculos repetidos para:
- resumo superior;
- listagem filtrada;
- custo das peças;
- filamentos/cores exibidos nos detalhes.

Alterações aplicadas:

## Resumo superior
- O cálculo de total de pedidos, abertos, faturamento, lucro e ticket médio agora usa cache curto.
- O cache é limpo automaticamente quando há gravação/edição/exclusão.

## Listagem de pedidos
- A lista base de pedidos agora é carregada com cache curto.
- A busca filtra os pedidos em memória.
- Evita nova consulta SQL a cada interação simples.

## Custos das peças nos pedidos
- Custos das peças usadas nos pedidos agora usam cache curto.
- Mantido o cálculo em lote já criado no v09.01.

## Detalhes dos pedidos
- Filamentos/cores das peças agora são carregados em lote.
- Removida consulta por pedido dentro do loop da listagem.

## Novo Pedido
- O custo da peça selecionada usa a função de custo cacheada.
- O resumo do novo pedido reutiliza esse custo.

Preservado:
- Visual aprovado.
- Mobile aprovado.
- Cálculos.
- Banco de dados.
- Regras de negócio.
- Edição, duplicação e exclusão.
- Novo pedido e cliente rápido.

Teste:
1. Rodar `streamlit run Dashboard.py`.
2. Abrir Pedidos.
3. Testar busca por:
   - pedido;
   - cliente;
   - peça;
   - status;
   - canal.
4. Abrir detalhes de alguns pedidos.
5. Criar um novo pedido.
6. Editar, duplicar ou excluir se possível.
7. Conferir se totais e lucros continuam coerentes.
