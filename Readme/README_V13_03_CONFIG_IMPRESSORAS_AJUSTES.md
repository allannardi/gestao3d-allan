# V13.03 — Ajustes em Configurações e Impressoras

## Alterações solicitadas

1. Cards superiores reorganizados:
- Impressoras
- Markup Padrão
- Pós Processamento
- Meta Lucro/hora
- Valor do KWh

2. Parâmetros Gerais:
- Adicionado campo `Valor do kWh (R$)`.
- Removido o aviso azul sobre energia/depreciação ficarem na impressora.
- Ao salvar o valor do kWh, o sistema recalcula energia/hora das impressoras com base no consumo cadastrado.

3. Impressoras:
- Primeiro mostra as impressoras cadastradas.
- Abaixo aparece o botão `+ Adicionar nova impressora`.
- Ao clicar, abre o formulário `Nova impressora`.

4. Removida a seção:
- `Como esses parâmetros são usados`.

## Banco
- Adicionada coluna `valor_kwh` na tabela `configuracoes`.

## Segurança
- Não apaga dados.
- Não altera pedidos existentes.
- Não altera peças existentes.
- Apenas ajusta layout, parâmetros gerais e cálculo de energia/hora das impressoras ao salvar o kWh.
