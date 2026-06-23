# Gestão 3D Allan v10.02 - Pós-processamento corrigido

Correção:
- Corrigido erro na tela Pedidos:
  `IndexError: tuple index out of range`.

Causa:
- A função de cálculo em lote dos pedidos já estava esperando o campo
  `tempo_pos_processamento_min`, mas a consulta SQL da página Pedidos ainda
  não trazia esse campo.

Correção aplicada:
- A consulta em lote da página Pedidos agora traz `tempo_pos_processamento_min`.
- O custo de pós-processamento também entra no cálculo em lote dos pedidos.

Mantido:
- Configurações funcionando.
- Peças funcionando.
- Cálculo de pós-processamento.
- Dados preservados.
- Banco sem alteração destrutiva.
