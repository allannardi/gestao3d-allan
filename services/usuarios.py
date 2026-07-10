from datetime import datetime

from database import conectar
from components.auth import (
    PERFIL_ADMIN,
    PERFIL_OPERADOR,
    STATUS_ATIVO,
    STATUS_INATIVO,
    gerar_senha_hash_usuario,
    label_perfil,
)


PERFIS_USUARIO = [PERFIL_ADMIN, PERFIL_OPERADOR]
PERFIS_USUARIO_LABELS = {perfil: label_perfil(perfil) for perfil in PERFIS_USUARIO}
STATUS_USUARIO = [STATUS_ATIVO, STATUS_INATIVO]


def _agora_sql():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def normalizar_email(email):
    # Campo mantido como email no banco por compatibilidade, mas agora representa usuário/login livre.
    return str(email or "").strip().lower()


def normalizar_texto(valor):
    return str(valor or "").strip()


def _row_para_dict(row):
    if not row:
        return None

    return {
        "id": row[0],
        "nome": row[1],
        "email": row[2],
        "perfil": row[3] or PERFIL_OPERADOR,
        "status": row[4] or STATUS_ATIVO,
        "data_criacao": row[5],
        "ultimo_login": row[6],
    }


def listar_usuarios():
    conn = conectar()
    rows = conn.execute("""
        SELECT
            id,
            nome,
            email,
            perfil,
            status,
            data_criacao,
            ultimo_login
        FROM usuarios
        ORDER BY
            CASE status WHEN 'Ativo' THEN 0 ELSE 1 END,
            CASE perfil WHEN 'Admin' THEN 0 ELSE 1 END,
            nome COLLATE NOCASE ASC
    """).fetchall()
    conn.close()
    return [_row_para_dict(row) for row in rows]


def obter_usuario(usuario_id):
    conn = conectar()
    row = conn.execute("""
        SELECT
            id,
            nome,
            email,
            perfil,
            status,
            data_criacao,
            ultimo_login
        FROM usuarios
        WHERE id = ?
        LIMIT 1
    """, (usuario_id,)).fetchone()
    conn.close()
    return _row_para_dict(row)


def email_em_uso(email, usuario_id_ignorar=None):
    email = normalizar_email(email)
    conn = conectar()

    if usuario_id_ignorar:
        row = conn.execute("""
            SELECT id
            FROM usuarios
            WHERE LOWER(email) = LOWER(?)
              AND id <> ?
            LIMIT 1
        """, (email, usuario_id_ignorar)).fetchone()
    else:
        row = conn.execute("""
            SELECT id
            FROM usuarios
            WHERE LOWER(email) = LOWER(?)
            LIMIT 1
        """, (email,)).fetchone()

    conn.close()
    return row is not None


def contar_admins_ativos(excluir_usuario_id=None):
    conn = conectar()

    if excluir_usuario_id:
        total = conn.execute("""
            SELECT COUNT(*)
            FROM usuarios
            WHERE perfil = ?
              AND status = ?
              AND id <> ?
        """, (PERFIL_ADMIN, STATUS_ATIVO, excluir_usuario_id)).fetchone()[0]
    else:
        total = conn.execute("""
            SELECT COUNT(*)
            FROM usuarios
            WHERE perfil = ?
              AND status = ?
        """, (PERFIL_ADMIN, STATUS_ATIVO)).fetchone()[0]

    conn.close()
    return int(total or 0)


def validar_campos_usuario(nome, email, perfil, status):
    nome = normalizar_texto(nome)
    email = normalizar_email(email)
    perfil = normalizar_texto(perfil)
    status = normalizar_texto(status)

    if not nome:
        return False, "Informe o nome do usuário."

    if not email:
        return False, "Informe o usuário/login."

    if perfil not in PERFIS_USUARIO:
        return False, "Perfil inválido."

    if status not in STATUS_USUARIO:
        return False, "Status inválido."

    return True, "OK"


def criar_usuario(nome, email, senha_temporaria, perfil=PERFIL_OPERADOR, status=STATUS_ATIVO):
    nome = normalizar_texto(nome)
    email = normalizar_email(email)
    senha_temporaria = str(senha_temporaria or "")
    perfil = normalizar_texto(perfil) or PERFIL_OPERADOR
    status = normalizar_texto(status) or STATUS_ATIVO

    ok, mensagem = validar_campos_usuario(nome, email, perfil, status)
    if not ok:
        return False, mensagem

    if len(senha_temporaria) < 4:
        return False, "A senha temporária precisa ter pelo menos 4 caracteres."

    if email_em_uso(email):
        return False, "Já existe um usuário com este login."

    senha_hash = gerar_senha_hash_usuario(senha_temporaria)
    agora = _agora_sql()

    conn = conectar()
    conn.execute("""
        INSERT INTO usuarios
        (
            nome,
            email,
            senha_hash,
            perfil,
            status,
            data_criacao,
            ultimo_login
        )
        VALUES (?, ?, ?, ?, ?, ?, NULL)
    """, (nome, email, senha_hash, perfil, status, agora))
    conn.commit()
    conn.close()

    return True, "Usuário criado com sucesso."


def atualizar_usuario(usuario_id, nome, email, perfil, status, usuario_atual_id=None):
    usuario = obter_usuario(usuario_id)
    if not usuario:
        return False, "Usuário não encontrado."

    nome = normalizar_texto(nome)
    email = normalizar_email(email)
    perfil = normalizar_texto(perfil) or PERFIL_OPERADOR
    status = normalizar_texto(status) or STATUS_ATIVO

    ok, mensagem = validar_campos_usuario(nome, email, perfil, status)
    if not ok:
        return False, mensagem

    usuario_atual_id = int(usuario_atual_id or 0)
    usuario_id_int = int(usuario_id or 0)

    removendo_admin_ativo = (
        usuario.get("perfil") == PERFIL_ADMIN
        and usuario.get("status") == STATUS_ATIVO
        and (perfil != PERFIL_ADMIN or status != STATUS_ATIVO)
    )

    if removendo_admin_ativo and contar_admins_ativos(excluir_usuario_id=usuario_id_int) == 0:
        return False, "Não é possível remover ou inativar o último Admin da Empresa ativo."

    if usuario_atual_id == usuario_id_int and status != STATUS_ATIVO:
        return False, "Você não pode inativar o próprio usuário logado."

    if usuario_atual_id == usuario_id_int and perfil != PERFIL_ADMIN:
        return False, "Você não pode remover o próprio perfil Admin da Empresa."

    if email_em_uso(email, usuario_id_ignorar=usuario_id_int):
        return False, "Já existe outro usuário com este login."

    conn = conectar()
    conn.execute("""
        UPDATE usuarios
        SET
            nome = ?,
            email = ?,
            perfil = ?,
            status = ?
        WHERE id = ?
    """, (nome, email, perfil, status, usuario_id_int))
    conn.commit()
    conn.close()

    return True, "Usuário atualizado com sucesso."


def redefinir_senha_usuario(usuario_id, nova_senha):
    usuario = obter_usuario(usuario_id)
    if not usuario:
        return False, "Usuário não encontrado."

    nova_senha = str(nova_senha or "")
    if len(nova_senha) < 4:
        return False, "A nova senha temporária precisa ter pelo menos 4 caracteres."

    senha_hash = gerar_senha_hash_usuario(nova_senha)

    conn = conectar()
    conn.execute("""
        UPDATE usuarios
        SET senha_hash = ?
        WHERE id = ?
    """, (senha_hash, usuario_id))
    conn.commit()
    conn.close()

    return True, "Senha redefinida com sucesso."


def resumo_usuarios():
    usuarios = listar_usuarios()
    total = len(usuarios)
    ativos = len([u for u in usuarios if u.get("status") == STATUS_ATIVO])
    admins = len([u for u in usuarios if u.get("perfil") == PERFIL_ADMIN and u.get("status") == STATUS_ATIVO])
    operadores = len([u for u in usuarios if u.get("perfil") == PERFIL_OPERADOR and u.get("status") == STATUS_ATIVO])

    return {
        "total": total,
        "ativos": ativos,
        "admins": admins,
        "operadores": operadores,
    }
