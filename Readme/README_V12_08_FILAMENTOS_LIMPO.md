# V12.08 — Filamentos limpo

## Objetivo
Reforço da correção da tela Filamentos.

## Confirmado no arquivo final
- Não existe `montar_alertas_filamento_operador`.
- Não existe `Resumo do rolo`.
- O formulário possui `st.form_submit_button("Salvar Filamento")`.
- A validação de nome, cor, peso e valor da compra acontece apenas ao clicar em salvar.

## Observação importante
Se o erro antigo ainda aparecer localmente, significa que o arquivo local `pages/1_Filamentos.py` não foi substituído ou o app ainda está rodando com a versão anterior.
