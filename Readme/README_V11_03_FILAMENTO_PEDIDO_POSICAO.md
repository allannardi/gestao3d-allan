# Gestão 3D Allan v11.03 - Filamento deste pedido na posição 2

Objetivo:
Ajustar a ordem do fluxo de criação de pedido e renomear o item de filamento.

Alterações:

## Novo Pedido
- O item de filamento saiu da posição 4.
- Agora aparece na posição 2 como:
  `2. Filamento deste pedido`.

Nova sequência:
1. Cliente;
2. Filamento deste pedido;
3. Valores;
4. Acompanhamento.

Dentro da etapa 2, o usuário escolhe:
- peça;
- quantidade;
- filamento/rolo/cor usado no pedido.

## Editar Pedido
- O nome da seção também foi alterado para:
  `Filamento deste pedido`.

## Textos
- As mensagens de validação e detalhes foram ajustadas para o novo nome.

Preservado:
- fluxo de disponibilidade em gramas;
- seleção de filamento por pedido;
- cards de lucro na listagem;
- lucro/hora na criação do pedido;
- pós-processamento no cálculo;
- dados e banco preservados.
