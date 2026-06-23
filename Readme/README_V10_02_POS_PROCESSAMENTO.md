# Gestão 3D Allan v10.02 - Pós-processamento no cálculo

Objetivo:
Fazer o campo "tempo de pós-processamento" participar dos cálculos de custo, preço sugerido, lucro e lucro/hora.

Alterações:

## Configurações
Adicionado novo parâmetro:
- Pós-processamento (R$/hora)

Esse valor representa o custo da hora de trabalho manual após a impressão.

Padrão da migração:
- R$ 0,00/hora

Isso preserva os valores atuais até você configurar um valor.

## Peças
O cálculo da peça agora considera:
- Material;
- Energia;
- Depreciação;
- Pós-processamento;
- Embalagem;
- Acessórios.

O tempo total da peça agora considera:
- tempo de impressão;
- tempo de pós-processamento convertido de minutos para horas.

## Pedidos
O custo da peça usada no pedido também passa a considerar o pós-processamento.

## Dashboard e resultados
Atualizados:
- Dashboard / Início;
- resultados de clientes;
- resultados de filamentos.

## Banco de dados
Migração segura:
- adiciona a coluna `custo_pos_processamento_hora` na tabela `configuracoes`;
- não apaga dados;
- não recria tabelas;
- não altera cadastros existentes.

Teste:
1. Faça backup de `database/atelie.db`.
2. Rode `streamlit run Dashboard.py`.
3. Abra Configurações.
4. Defina um valor em "Pós-processamento (R$/hora)".
5. Abra uma peça com tempo de pós-processamento preenchido.
6. Confira se o custo/preço/lucro muda.
7. Confira Pedidos e Início.
