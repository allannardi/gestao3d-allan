# Gestão 3D — v15.03

## Nome da empresa/projeto na sidebar

Esta versão adiciona o nome da empresa/projeto abaixo do logo **Gestão 3D** na sidebar.

## O que entrou

- Versão atualizada para `0.15.03`.
- `SCHEMA_VERSION` atualizado para `v15_03_nome_empresa_sidebar`.
- Nova coluna segura `nome_empresa` na tabela `configuracoes`.
- Novo service `services/empresa.py`.
- Sidebar agora exibe o nome da empresa/projeto abaixo do título **Gestão 3D**.
- Configurações ganhou uma área Admin chamada **Empresa / Projeto**.
- Apenas Admin consegue editar o nome da empresa/projeto.
- Operador continua sem ver áreas administrativas.

## O que validar

1. Entrar como Admin.
2. Confirmar que a sidebar mostra `0.15.03`.
3. Abrir **Configurações**.
4. Encontrar a área **Empresa / Projeto**.
5. Alterar o nome da empresa/projeto.
6. Confirmar que o nome aparece abaixo do logo na sidebar.
7. Sair e entrar como Operador.
8. Confirmar que o nome continua aparecendo na sidebar.
9. Confirmar que Operador não consegue editar a área **Empresa / Projeto**.

## Observação

O valor padrão é **Minha empresa** até o Admin alterar o nome.
