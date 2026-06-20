# Gestão 3D Allan v07.16 - Resultados em Clientes e Filamentos

Alterações:

## Clientes
Dentro de cada cliente cadastrado, agora aparece:
- total de pedidos vinculados;
- pedidos em aberto;
- faturamento dos pedidos não cancelados;
- lucro estimado;
- quantidade total vendida;
- ticket médio;
- lista dos pedidos vinculados ao cliente.

## Filamentos
Dentro de cada filamento cadastrado, agora aparece:
- total de pedidos vinculados;
- peças vinculadas ao filamento;
- faturamento dos pedidos vinculados;
- lucro estimado;
- quantidade vendida;
- consumo estimado em gramas;
- lista dos pedidos vinculados ao filamento.

## Técnico
- Criado componente `components/item_results.py`.
- Os cálculos usam a mesma lógica de custo das peças/pedidos.
- Para filamentos com múltiplas cores em uma peça, o consumo estimado considera o peso do filamento no lote.
- Os pedidos cancelados aparecem na lista, mas não entram no faturamento/lucro/quantidade.
- Desktop e mobile preservados.

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Abrir Clientes > Detalhes e ações
3. Conferir resultados e pedidos do cliente
4. Abrir Filamentos > Detalhes, peças vinculadas e ações
5. Conferir resultados e pedidos vinculados ao filamento
