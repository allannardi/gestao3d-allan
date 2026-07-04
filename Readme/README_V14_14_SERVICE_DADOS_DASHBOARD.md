# V14.14 — Service de dados da Dashboard

## Objetivo
Continuar a fase 2 do roadmap: simplificar e separar regras internas.

## Alteração principal
Foi criado o service `services/dashboard_dados.py` para centralizar as consultas de banco usadas pela Dashboard.

## O que foi separado
A Dashboard agora delega para o service:
- carregamento das configurações;
- carregamento dos pedidos;
- contadores de clientes, peças, filamentos e impressoras;
- carregamento de impressoras ativas;
- carregamento da impressora padrão.

## O que não mudou
- Visual.
- Banco de dados.
- Gráficos.
- Indicadores.
- Cálculos.
- Regras de negócio.
- Layout mobile e desktop.

## Observação
Esta versão reduz SQL direto dentro da tela Dashboard e prepara melhor o código para uma futura API/backend.
