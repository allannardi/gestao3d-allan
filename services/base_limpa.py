from database import conectar


TABELAS_OPERACIONAIS = [
    ("impressoras", "Impressoras"),
    ("filamentos", "Filamentos"),
    ("pecas", "Peças"),
    ("clientes", "Clientes"),
    ("acessorios", "Acessórios"),
    ("pedidos", "Pedidos"),
]

TABELAS_TECNICAS_PERMITIDAS = [
    ("configuracoes", "Configurações da empresa"),
    ("usuarios", "Usuários de acesso"),
    ("categorias_pecas", "Categorias padrão"),
    ("auth_config", "Compatibilidade do login antigo"),
]


REGRAS_BASE_NOVA = [
    {
        "item": "Configurações técnicas",
        "regra": "Permitido",
        "descricao": "A base pode nascer com configurações padrão, identidade técnica e categorias de apoio.",
    },
    {
        "item": "Usuário Admin da Empresa",
        "regra": "Permitido",
        "descricao": "A base precisa ter pelo menos um Admin da Empresa para iniciar a implantação.",
    },
    {
        "item": "Impressoras",
        "regra": "Manual",
        "descricao": "A primeira impressora deve ser cadastrada pelo Admin da Empresa. O sistema não cria impressora automática.",
    },
    {
        "item": "Filamentos",
        "regra": "Manual",
        "descricao": "O primeiro filamento deve ser cadastrado pela empresa durante a trilha inicial.",
    },
    {
        "item": "Peças, clientes, acessórios e pedidos",
        "regra": "Manual",
        "descricao": "Esses dados nunca devem nascer automaticamente em uma nova base de empresa.",
    },
]


def obter_regras_base_nova():
    return list(REGRAS_BASE_NOVA)


def _contar_tabela(conn, tabela):
    try:
        return int(conn.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0] or 0)
    except Exception:
        return 0


def obter_diagnostico_base_limpa():
    """Diagnóstico para validar se uma base nova começa sem dados operacionais.

    No modelo futuro escolhido, uma nova empresa terá um banco separado.
    Esse banco pode ter tabelas técnicas e usuário Admin inicial, mas não deve
    receber automaticamente impressoras, peças, filamentos, clientes ou pedidos.
    """
    conn = conectar()

    operacionais = []
    total_operacional = 0
    for tabela, label in TABELAS_OPERACIONAIS:
        total = _contar_tabela(conn, tabela)
        total_operacional += total
        operacionais.append({
            "tabela": tabela,
            "label": label,
            "total": total,
            "limpo": total == 0,
        })

    tecnicas = []
    for tabela, label in TABELAS_TECNICAS_PERMITIDAS:
        tecnicas.append({
            "tabela": tabela,
            "label": label,
            "total": _contar_tabela(conn, tabela),
        })

    try:
        total_usuarios_ativos = int(conn.execute("""
            SELECT COUNT(*)
            FROM usuarios
            WHERE COALESCE(status, 'Ativo') = 'Ativo'
        """).fetchone()[0] or 0)
        total_admins_ativos = int(conn.execute("""
            SELECT COUNT(*)
            FROM usuarios
            WHERE perfil = 'Admin'
              AND COALESCE(status, 'Ativo') = 'Ativo'
        """).fetchone()[0] or 0)
    except Exception:
        total_usuarios_ativos = 0
        total_admins_ativos = 0

    conn.close()

    usuarios = {
        "ativos": total_usuarios_ativos,
        "admins": total_admins_ativos,
    }

    return {
        "operacionais": operacionais,
        "tecnicas": tecnicas,
        "total_operacional": total_operacional,
        "base_operacional_limpa": total_operacional == 0,
        "usuarios": usuarios,
        "regras_base_nova": obter_regras_base_nova(),
        "seed_operacional_automatico": False,
    }
