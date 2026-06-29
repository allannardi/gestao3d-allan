# V13.12 — Datas de produção e entrega no pedido

## Objetivo
Criar datas operacionais para melhorar o controle dos pedidos e corrigir a base do gráfico de utilização das impressoras.

## Novas variáveis no pedido
- `data_final_producao`
- `data_entrega_real`

## Comportamento
- Ao mudar status de **Em Produção** para **Pronto**, o sistema abre o campo **Data Final Produção**.
- Ao mudar status de **Pronto** para **Entregue**, o sistema abre o campo **Data da Entrega**.
- Na edição completa do pedido, os campos aparecem quando o status exige a informação ou quando já existe data salva.

## Dashboard
- O gráfico **Utilização das impressoras por mês** passa a usar **Data Final Produção**.
- Pedidos antigos sem Data Final Produção continuam funcionando usando Data do Pedido como fallback.

## Segurança
- Não apaga dados.
- Não altera pedidos automaticamente.
- Não altera cálculos de preço.
- Adiciona apenas novas colunas e novos campos de controle.
