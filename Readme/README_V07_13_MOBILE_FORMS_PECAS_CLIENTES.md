# Gestão 3D Allan v07.13 - Mobile formulários de Peças e Clientes

Alterações:

## Peças
- Formulário de nova peça recebeu etapas visuais no celular:
  1. Identificação
  2. Filamentos e cores
  3. Produção e embalagem
  4. Acessórios
  5. Arquivos e observações
- Resumo da peça virou card em degradê no mobile.
- Resumo desktop preservado.
- Botão Salvar Peça mais destacado no celular.

## Clientes
- Formulário de novo cliente recebeu etapas visuais:
  1. Dados principais
  2. Contato e localização
  3. Observações
- Botão Salvar Cliente mais destacado no celular.
- Desktop preservado.

Nenhuma regra de cálculo foi alterada.
Nenhuma estrutura de banco foi alterada.

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Abrir Peças no mobile e clicar em + Nova Peça
3. Testar preenchimento completo e resumo
4. Abrir Clientes no mobile e clicar em + Novo Cliente
5. Testar preenchimento e salvamento
6. Confirmar desktop preservado
