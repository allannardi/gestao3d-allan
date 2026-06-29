# V13.11 — Aplicar impressora padrão em lote

## Objetivo
Criar uma ação segura para vincular a impressora padrão aos pedidos antigos que ainda não possuem impressora.

## Onde fica
Configurações > Impressoras > Ajuste em lote

## Como funciona
- O sistema conta pedidos com `impressora_id` vazio.
- Mostra a impressora padrão atual.
- Exige confirmação por checkbox.
- Ao clicar, atualiza apenas pedidos sem impressora.
- Pedidos que já têm impressora não são alterados.

## Segurança
- Não apaga dados.
- Não altera pedidos que já possuem impressora.
- Não altera peças, clientes, filamentos ou cálculos.
- A ação só executa após confirmação.
