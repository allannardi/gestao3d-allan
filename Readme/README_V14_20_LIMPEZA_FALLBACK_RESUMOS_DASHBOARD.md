# V14.20 — Limpeza do fallback antigo de resumos da Dashboard

## Objetivo
Continuar a fase 2 do roadmap: simplificar e separar regras internas.

## Alteração principal
Após a validação das versões anteriores, removemos da `Dashboard.py` o bloco antigo de fallback responsável por montar os resumos diretamente dentro da tela.

Agora a Dashboard depende do service validado:

- `services/dashboard_resumos.py`

## O que saiu da Dashboard
Foi removido o fallback local que recriava dentro da tela:
- pedidos abertos;
- faturamento total;
- lucro total;
- horas vendidas;
- quantidade de peças;
- resumo por status;
- resumo por peça;
- resumo por cliente;
- resumo por impressora;
- dados de vendas por mês;
- dados de utilização por impressora;
- distribuição do faturamento.

## O que não mudou
- Visual.
- Banco de dados.
- Filtros.
- Gráfico de rosca.
- Indicadores.
- Cálculos.
- Regras de negócio.
- Layout mobile e desktop.

## Observação
Esta versão reduz a complexidade da `Dashboard.py` e consolida a regra de resumo no service já validado.
