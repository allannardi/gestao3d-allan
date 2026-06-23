# Gestão 3D Allan v10.01 - Datas em DD/MM/AAAA e troca de senha

Objetivo:
Aplicar duas melhorias solicitadas sem apagar dados cadastrados.

## Datas
- Criado `components/formatters.py`.
- Datas passam a ser exibidas no formato brasileiro `DD/MM/AAAA`.
- O banco não é recriado e os valores salvos continuam preservados.
- A função aceita datas antigas em `AAAA-MM-DD` e também datas digitadas em `DD/MM/AAAA`.

Locais ajustados:
- Dashboard/Início;
- Pedidos;
- Clientes;
- Filamentos;
- Peças;
- Resultados internos de cliente/filamento.

## Troca de senha
- Criada tabela segura `auth_config`, sem apagar nenhuma tabela existente.
- A senha personalizada é salva no banco atual.
- A senha é armazenada com hash PBKDF2 + salt, não em texto puro.
- Configurações agora tem a seção `Acesso e senha`.

Fluxo:
1. Entre com a senha atual.
2. Vá em Configurações.
3. Informe senha atual, nova senha e confirmação.
4. Salve.
5. No próximo login, use a nova senha.

Preservado:
- Todos os cadastros existentes;
- banco `database/atelie.db`;
- Turso online;
- visual aprovado;
- mobile aprovado;
- cálculos e regras de negócio.

Recomendação antes de testar localmente:
Copiar `database/atelie.db` para backup.
