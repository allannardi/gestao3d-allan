# Gestão 3D Allan v05 - Filamentos no cadastro da peça

Correção de regra de negócio:

- A escolha de múltiplos filamentos/cores saiu da criação do pedido.
- Agora múltiplos filamentos/cores são definidos no cadastro e edição da peça.
- Cada filamento tem peso próprio no lote.
- O peso total da peça passa a ser calculado pela soma dos pesos dos filamentos.
- O custo de material passa a considerar o custo/grama de cada filamento usado.
- Pedido, Dashboard e card de Peças usam esse custo corrigido.

Observação:
A tabela antiga `pedido_filamentos` permanece no banco para compatibilidade, mas deixou de ser usada nas novas telas.
