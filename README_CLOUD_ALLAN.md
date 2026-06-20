# Gestão 3D Cloud - Allan

Esta pasta contém a primeira versão preparada para rodar local ou em nuvem.

## O que mudou

- A conexão com o banco foi centralizada em `database.py`.
- Localmente, o app continua usando `database/atelie.db`.
- Na nuvem, o app pode usar Turso/libSQL usando secrets.
- As páginas passaram a usar `from database import conectar`.
- `requirements.txt` foi criado para instalação das dependências no Streamlit Cloud.
- `.gitignore` evita subir banco local e segredos para o GitHub.
- `.streamlit/config.toml` mantém a navegação padrão do Streamlit oculta.

## Teste local

1. Copie estes arquivos para a raiz do projeto.
2. Confirme que o arquivo `.streamlit/secrets.toml` existe localmente com seu usuário e senha.
3. Rode:

```bash
streamlit run Dashboard.py
```

## Secrets local

Use o arquivo `secrets_exemplo.toml` apenas como modelo.
Não envie `.streamlit/secrets.toml` para o GitHub.

## Próximo passo

Depois que o teste local estiver ok, criaremos o banco Turso do Allan e configuraremos os secrets da versão cloud.
