# Gestão 3D Allan v11.04 - Status rápido do pedido

Objetivo:
Permitir alterar o status do pedido diretamente na listagem, sem abrir Detalhes e sem entrar em Editar.

Alterações:

## Listagem de Pedidos
- Adicionado seletor "Alterar status sem abrir detalhes" logo abaixo do card principal do pedido.
- Adicionado botão "Salvar status".
- O botão fica desabilitado quando o status selecionado é igual ao status atual.
- Ao salvar, o sistema:
  - atualiza o status no banco;
  - limpa o cache;
  - recarrega a tela.

## Impactos preservados
- Se o pedido for marcado como Cancelado, os cálculos que ignoram pedidos cancelados continuam funcionando.
- O controle de disponibilidade de filamento continua respeitando pedidos cancelados.
- O modo Editar continua existindo para alterações completas.

Preservado:
- Filamento deste pedido;
- cards de lucro na listagem;
- lucro/hora no novo pedido;
- pós-processamento no cálculo;
- datas em DD/MM/AAAA;
- banco e dados preservados.
