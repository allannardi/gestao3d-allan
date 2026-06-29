# V12.09 — Acessórios e Clientes operator friendly

## Base
Criado a partir da V12.08 aprovada.

## Acessórios
- Adicionado texto discreto explicando que o custo deve ser unitário.
- Adicionados helps em:
  - Nome do Acessório;
  - Categoria;
  - Custo Unitário;
  - Observações.
- Validação reforçada:
  - nome obrigatório;
  - custo unitário maior que zero.
- Mensagem de sucesso agora informa que o acessório já pode ser usado em peças.

## Clientes
- Adicionado texto discreto explicando que apenas o nome é obrigatório.
- Adicionados helps em:
  - Nome do Cliente;
  - Tipo;
  - CPF/CNPJ;
  - Telefone/WhatsApp;
  - Cidade;
  - Instagram;
  - E-mail;
  - Estado;
  - Origem;
  - Observações.
- Se o cliente for salvo sem telefone, e-mail ou Instagram, o sistema exibe uma dica, mas não bloqueia o cadastro.
- Mensagem de sucesso agora informa que o cliente já pode ser usado em pedidos.

## Segurança
- Não altera banco de dados.
- Não cria tabela.
- Não altera cálculos.
- Não altera registros já cadastrados.
