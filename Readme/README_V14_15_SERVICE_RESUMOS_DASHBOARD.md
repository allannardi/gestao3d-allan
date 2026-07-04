# V14.15 — Service de resumos da Dashboard

## Objetivo
Continuar a fase 2 do roadmap: simplificar e separar regras internas.

## Alteração principal
Foi criado o service `services/dashboard_resumos.py` para centralizar a montagem dos indicadores da Dashboard.

## O que foi separado
A Dashboard agora delega para o novo service:
- contagem de pedidos abertos;
- faturamento total;
- lucro total;
- horas vendidas;
- quantidade de peças;
- faturamento e lucro do mês;
- resumo por status;
- resumo por peça;
- resumo por cliente;
- resumo por impressora;
- dados do gráfico de vendas por mês;
- dados do gráfico de utilização por impressora.

## O que não mudou
- Visual.
- Banco de dados.
- Gráficos.
- Indicadores.
- Cálculos.
- Regras de negócio.
- Layout mobile e desktop.

## Observação
Esta versão reduz bastante regra de negócio dentro do arquivo `Dashboard.py` e deixa a tela mais próxima de apenas renderizar informações.
