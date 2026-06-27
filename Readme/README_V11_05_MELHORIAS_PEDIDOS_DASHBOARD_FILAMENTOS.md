# V11.05 - Melhorias em Pedidos, Dashboard e Filamentos

Alterações incluídas:

1. Pedidos
- Adicionado filtro de status na aba Pedidos.
- Status `Confirmado` renomeado para `Encomendado`.
- Migração segura: pedidos antigos com status `Confirmado` são atualizados para `Encomendado`.

2. Dashboard / Início
- Corrigido o Resumo Executivo: o lucro estimado do mês agora usa o lucro do mês, não o lucro total.
- Adicionada tabela `Vendas por mês` com mês, pedidos, peças, faturamento e lucro.

3. Filamentos
- Corrigido resultado do filamento para considerar somente a participação do filamento usado no pedido.
- O faturamento e lucro do filamento agora são proporcionais ao peso usado no pedido, em vez de somar o pedido inteiro.

Observações:
- Nenhuma tabela foi apagada.
- Nenhum dado foi recriado.
- A alteração de status é feita por UPDATE seguro.
