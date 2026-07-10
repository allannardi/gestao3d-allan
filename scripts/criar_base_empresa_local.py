"""
Cria uma base SQLite local separada para uma nova empresa do Gestão 3D.

Uso recomendado, a partir da pasta raiz do projeto:

python scripts/criar_base_empresa_local.py --codigo empresa-teste --nome "Empresa Teste" --admin-login admin --admin-senha 1234

A regra deste script é segura:
- cria um novo arquivo .db separado;
- não altera a base atual;
- não apaga dados;
- não cria dados operacionais automáticos;
- cria somente estrutura técnica, configurações, categorias de apoio e Admin da Empresa inicial.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import secrets as secrets_lib
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


STATUS_IMPLANTACAO_PADRAO = "Em implantação"
AMBIENTE_PADRAO = "Teste"
PERFIL_ADMIN = "Admin"
STATUS_ATIVO = "Ativo"
ITERACOES_HASH_SENHA = 200_000
TABELAS_OPERACIONAIS = [
    "impressoras",
    "filamentos",
    "pecas",
    "clientes",
    "acessorios",
    "pedidos",
]


MAPA_ACENTOS = str.maketrans({
    "á": "a", "à": "a", "ã": "a", "â": "a", "ä": "a",
    "é": "e", "ê": "e", "è": "e", "ë": "e",
    "í": "i", "ì": "i", "î": "i", "ï": "i",
    "ó": "o", "ò": "o", "ô": "o", "õ": "o", "ö": "o",
    "ú": "u", "ù": "u", "û": "u", "ü": "u",
    "ç": "c",
})


def normalizar_codigo(valor: str) -> str:
    texto = str(valor or "").strip().lower().translate(MAPA_ACENTOS)
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    texto = re.sub(r"-+", "-", texto).strip("-")
    return texto[:40] or "empresa"


def perguntar(rotulo: str, padrao: str = "", obrigatorio: bool = False, senha: bool = False) -> str:
    import getpass

    while True:
        sufixo = f" [{padrao}]" if padrao else ""
        prompt = f"{rotulo}{sufixo}: "
        valor = getpass.getpass(prompt) if senha else input(prompt)
        valor = str(valor or padrao or "").strip()
        if valor or not obrigatorio:
            return valor
        print("Campo obrigatório.")


def montar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cria uma base SQLite local separada para uma nova empresa do Gestão 3D."
    )
    parser.add_argument("--codigo", help="Código curto da empresa/base. Ex.: empresa-teste")
    parser.add_argument("--nome", help="Nome da empresa/projeto")
    parser.add_argument("--admin-login", help="Login do Admin da Empresa inicial")
    parser.add_argument("--admin-senha", help="Senha inicial do Admin da Empresa")
    parser.add_argument("--responsavel", default="", help="Responsável pela empresa/projeto")
    parser.add_argument("--telefone", default="", help="Telefone/WhatsApp")
    parser.add_argument("--cidade-uf", default="", help="Cidade/UF")
    parser.add_argument("--ambiente", default=AMBIENTE_PADRAO, choices=["Operação", "Teste", "Homologação"], help="Ambiente da base")
    parser.add_argument("--path", help="Caminho do arquivo .db. Se omitido, usa database/<codigo>.db")
    return parser


def carregar_dados(args: argparse.Namespace) -> dict:
    nome = args.nome or perguntar("Nome da empresa/projeto", obrigatorio=True)
    codigo_padrao = normalizar_codigo(args.codigo or nome)
    codigo = normalizar_codigo(args.codigo or perguntar("Código interno da empresa/base", codigo_padrao, obrigatorio=True))
    admin_login = args.admin_login or perguntar("Login Admin da Empresa", "admin", obrigatorio=True)
    admin_senha = args.admin_senha or perguntar("Senha inicial do Admin da Empresa", obrigatorio=True, senha=True)

    if len(admin_senha) < 4:
        raise ValueError("A senha inicial precisa ter pelo menos 4 caracteres.")

    caminho = Path(args.path) if args.path else PROJECT_ROOT / "database" / f"{codigo}.db"
    if not caminho.is_absolute():
        caminho = PROJECT_ROOT / caminho

    return {
        "nome": nome.strip(),
        "codigo": codigo,
        "admin_login": admin_login.strip().lower(),
        "admin_senha": admin_senha,
        "responsavel": str(args.responsavel or "").strip(),
        "telefone": str(args.telefone or "").strip(),
        "cidade_uf": str(args.cidade_uf or "").strip(),
        "ambiente": args.ambiente or AMBIENTE_PADRAO,
        "caminho": caminho,
    }


def inicializar_estrutura(caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    os.environ["GESTAO3D_LOCAL_DB_PATH"] = str(caminho)
    os.environ["DATABASE_MODE"] = "local"

    # Importar depois de definir GESTAO3D_LOCAL_DB_PATH garante que as migrations
    # rodem no arquivo novo, e não na base atualmente usada pelo projeto.
    from database import (
        criar_banco,
        garantir_migracoes,
        inserir_configuracao_padrao,
        inserir_categorias_pecas_padrao,
    )

    criar_banco()
    garantir_migracoes()
    inserir_configuracao_padrao()
    inserir_categorias_pecas_padrao()


def gerar_senha_hash_usuario(senha: str) -> str:
    salt = secrets_lib.token_hex(16)
    senha_hash = hashlib.pbkdf2_hmac(
        "sha256",
        str(senha).encode("utf-8"),
        salt.encode("utf-8"),
        ITERACOES_HASH_SENHA,
    ).hex()
    return f"pbkdf2_sha256${ITERACOES_HASH_SENHA}${salt}${senha_hash}"


def gerar_base_empresa_id() -> str:
    return f"g3d-{uuid4().hex[:12]}"


def gravar_dados_empresa(dados: dict) -> None:
    caminho = dados["caminho"]
    conn = sqlite3.connect(str(caminho))
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    codigo = normalizar_codigo(dados["codigo"])
    base_empresa_id = gerar_base_empresa_id()

    conn.execute("""
        UPDATE configuracoes
        SET
            nome_empresa = ?,
            login_admin_empresa = ?,
            responsavel_empresa = ?,
            telefone_whatsapp_empresa = ?,
            cidade_uf_empresa = ?,
            status_implantacao = ?,
            base_empresa_id = ?,
            codigo_empresa = ?,
            ambiente_base = ?
    """, (
        dados["nome"],
        dados["admin_login"],
        dados["responsavel"],
        dados["telefone"],
        dados["cidade_uf"],
        STATUS_IMPLANTACAO_PADRAO,
        base_empresa_id,
        codigo,
        dados["ambiente"],
    ))

    senha_hash = gerar_senha_hash_usuario(dados["admin_senha"])
    conn.execute("DELETE FROM usuarios")
    conn.execute("""
        INSERT INTO usuarios
        (nome, email, senha_hash, perfil, status, data_criacao, ultimo_login)
        VALUES (?, ?, ?, ?, ?, ?, NULL)
    """, (
        "Administrador da Empresa",
        dados["admin_login"],
        senha_hash,
        PERFIL_ADMIN,
        STATUS_ATIVO,
        agora,
    ))

    conn.commit()
    conn.close()


def validar_base_limpa(caminho: Path) -> tuple[bool, dict]:
    conn = sqlite3.connect(str(caminho))
    totais = {}
    for tabela in TABELAS_OPERACIONAIS:
        try:
            totais[tabela] = int(conn.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0] or 0)
        except Exception:
            totais[tabela] = -1
    try:
        usuarios = int(conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] or 0)
    except Exception:
        usuarios = 0
    conn.close()

    ok_operacional = all(total == 0 for total in totais.values())
    ok_usuario = usuarios >= 1
    return ok_operacional and ok_usuario, {"operacionais": totais, "usuarios": usuarios}


def imprimir_resultado(dados: dict, validacao: dict) -> None:
    caminho = dados["caminho"]
    try:
        caminho_config = caminho.relative_to(PROJECT_ROOT)
    except ValueError:
        caminho_config = caminho

    print("\nBase da empresa criada com sucesso.")
    print(f"Empresa/projeto: {dados['nome']}")
    print(f"Código: {dados['codigo']}")
    print(f"Arquivo: {caminho}")
    print(f"Login Admin da Empresa: {dados['admin_login']}")
    print("Dados operacionais criados automaticamente: 0")
    print(f"Usuários criados: {validacao.get('usuarios')}")

    print("\nPara abrir esta base no Gestão 3D local, configure .streamlit/secrets.toml assim:")
    print("\n[database]")
    print('mode = "local"')
    print(f'local_path = "{str(caminho_config).replace(chr(92), "/")}"')

    print("\nDepois rode:")
    print("python -m streamlit run Dashboard.py")


def main() -> int:
    parser = montar_parser()
    args = parser.parse_args()

    try:
        dados = carregar_dados(args)
        caminho = dados["caminho"]

        if caminho.exists():
            print(f"\nERRO: o arquivo já existe: {caminho}")
            print("Por segurança, este script não sobrescreve bases existentes.")
            return 1

        inicializar_estrutura(caminho)
        gravar_dados_empresa(dados)
        ok, validacao = validar_base_limpa(caminho)

        if not ok:
            print("\nERRO: a base foi criada, mas a validação final encontrou pendências.")
            print(validacao)
            return 2

        imprimir_resultado(dados, validacao)
        return 0

    except KeyboardInterrupt:
        print("\nOperação cancelada.")
        return 130
    except Exception as exc:
        print(f"\nERRO: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
