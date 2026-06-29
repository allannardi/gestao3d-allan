# V13.00 — Gestão de Impressoras Base

## Objetivo
Criar a base segura para gestão de impressoras dentro de Configurações.

## Alterações estruturais
- Nova tabela `impressoras`.
- Primeira impressora cadastrada é marcada como padrão.
- Bancos antigos recebem automaticamente uma impressora padrão `IMP-001`.
- Sidebar atualizada para versão `0.13`.

## Campos da impressora
- Código automático: `IMP-001`, `IMP-002`, etc.
- Marca
- Modelo
- Status: Ativa/Inativa
- Consumo da impressora (W)
- Valor do kWh (R$)
- Energia/hora calculada automaticamente
- Depreciação/hora
- Observações
- Impressora padrão

## Modelos pré-definidos
- Bambu Lab A1 Mini
- Bambu Lab A1
- Creality Ender-3 V3 SE
- Creality Ender-3 V3 KE
- Anycubic Kobra 2 Neo
- Personalizada

## Configurações gerais
- `Margem padrão` foi renomeada visualmente para `Markup Padrão`.
- Energia/hora e depreciação/hora saíram da configuração geral e passaram para Impressoras.
- Meta lucro/hora e pós-processamento continuam como configurações gerais da empresa.

## Segurança
- Não altera pedidos existentes.
- Não altera peças existentes.
- Não exige escolher impressora no pedido ainda.
- Enquanto pedidos ainda não possuem impressora, os cálculos usam a impressora padrão.
