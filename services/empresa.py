from database import conectar, garantir_coluna


NOME_EMPRESA_PADRAO = "Minha empresa"
STATUS_IMPLANTACAO_OPCOES = [
    "Em implantação",
    "Em operação",
    "Em revisão",
    "Pausado",
]


CAMPOS_DADOS_EMPRESA = {
    "nome_empresa": "TEXT DEFAULT 'Minha empresa'",
    "login_admin_empresa": "TEXT DEFAULT ''",
    "responsavel_empresa": "TEXT DEFAULT ''",
    "telefone_whatsapp_empresa": "TEXT DEFAULT ''",
    "cidade_uf_empresa": "TEXT DEFAULT ''",
    "observacoes_internas_empresa": "TEXT DEFAULT ''",
    "status_implantacao": "TEXT DEFAULT 'Em implantação'",
}


def garantir_colunas_dados_empresa():
    """Adiciona os campos de Dados da Empresa sem alterar dados existentes."""
    for coluna, definicao in CAMPOS_DADOS_EMPRESA.items():
        try:
            garantir_coluna("configuracoes", coluna, definicao)
        except Exception:
            pass


def garantir_coluna_nome_empresa():
    """Compatibilidade com versões anteriores."""
    garantir_colunas_dados_empresa()


def _texto(valor):
    return str(valor or "").strip()


def normalizar_nome_empresa(nome):
    nome = _texto(nome)
    return nome if nome else NOME_EMPRESA_PADRAO


def normalizar_status_implantacao(status):
    status = _texto(status)
    return status if status in STATUS_IMPLANTACAO_OPCOES else STATUS_IMPLANTACAO_OPCOES[0]


def _buscar_login_admin_ativo():
    try:
        conn = conectar()
        row = conn.execute("""
        SELECT email
        FROM usuarios
        WHERE perfil = 'Admin'
          AND COALESCE(status, 'Ativo') = 'Ativo'
        ORDER BY id ASC
        LIMIT 1
        """).fetchone()
        conn.close()
        if row and row[0]:
            return _texto(row[0])
    except Exception:
        pass

    return "admin"


def obter_dados_empresa(fallback_login_admin=None):
    """Retorna os dados administrativos da empresa/projeto."""
    garantir_colunas_dados_empresa()

    fallback_login_admin = _texto(fallback_login_admin) or _buscar_login_admin_ativo()

    dados = {
        "nome_empresa": NOME_EMPRESA_PADRAO,
        "login_admin_empresa": fallback_login_admin,
        "responsavel_empresa": "",
        "telefone_whatsapp_empresa": "",
        "cidade_uf_empresa": "",
        "observacoes_internas_empresa": "",
        "status_implantacao": STATUS_IMPLANTACAO_OPCOES[0],
    }

    try:
        conn = conectar()
        row = conn.execute("""
        SELECT
            nome_empresa,
            login_admin_empresa,
            responsavel_empresa,
            telefone_whatsapp_empresa,
            cidade_uf_empresa,
            observacoes_internas_empresa,
            status_implantacao
        FROM configuracoes
        LIMIT 1
        """).fetchone()
        conn.close()

        if row:
            dados.update({
                "nome_empresa": normalizar_nome_empresa(row[0]),
                "login_admin_empresa": _texto(row[1]) or fallback_login_admin,
                "responsavel_empresa": _texto(row[2]),
                "telefone_whatsapp_empresa": _texto(row[3]),
                "cidade_uf_empresa": _texto(row[4]),
                "observacoes_internas_empresa": _texto(row[5]),
                "status_implantacao": normalizar_status_implantacao(row[6]),
            })
    except Exception:
        pass

    return dados


def obter_nome_empresa():
    """Retorna o nome exibido abaixo do logo na sidebar."""
    return obter_dados_empresa().get("nome_empresa", NOME_EMPRESA_PADRAO)


def dados_empresa_obrigatorios_configurados():
    """Confirma se os campos obrigatórios da implantação foram preenchidos."""
    dados = obter_dados_empresa()
    nome = _texto(dados.get("nome_empresa"))
    login = _texto(dados.get("login_admin_empresa"))

    return bool(
        nome
        and nome.lower() != NOME_EMPRESA_PADRAO.lower()
        and login
    )


def salvar_dados_empresa(
    nome_empresa,
    login_admin_empresa,
    responsavel_empresa="",
    telefone_whatsapp_empresa="",
    cidade_uf_empresa="",
    observacoes_internas_empresa="",
    status_implantacao="Em implantação",
):
    """Salva os dados administrativos da empresa/projeto."""
    nome_empresa = normalizar_nome_empresa(nome_empresa)
    login_admin_empresa = _texto(login_admin_empresa)
    responsavel_empresa = _texto(responsavel_empresa)
    telefone_whatsapp_empresa = _texto(telefone_whatsapp_empresa)
    cidade_uf_empresa = _texto(cidade_uf_empresa)
    observacoes_internas_empresa = _texto(observacoes_internas_empresa)
    status_implantacao = normalizar_status_implantacao(status_implantacao)

    if not nome_empresa or nome_empresa.lower() == NOME_EMPRESA_PADRAO.lower():
        return False, "Informe o nome da empresa/projeto.", None

    if not login_admin_empresa:
        return False, "Informe o login Admin da empresa.", None

    garantir_colunas_dados_empresa()

    conn = conectar()
    total = conn.execute("SELECT COUNT(*) FROM configuracoes").fetchone()[0]

    valores = (
        nome_empresa,
        login_admin_empresa,
        responsavel_empresa,
        telefone_whatsapp_empresa,
        cidade_uf_empresa,
        observacoes_internas_empresa,
        status_implantacao,
    )

    if int(total or 0) == 0:
        conn.execute("""
        INSERT INTO configuracoes
        (
            energia_hora,
            depreciacao_hora,
            margem_padrao,
            meta_lucro_hora,
            custo_pos_processamento_hora,
            valor_kwh,
            nome_empresa,
            login_admin_empresa,
            responsavel_empresa,
            telefone_whatsapp_empresa,
            cidade_uf_empresa,
            observacoes_internas_empresa,
            status_implantacao
        )
        VALUES (0.15, 0.75, 150, 5, 0, 0.65, ?, ?, ?, ?, ?, ?, ?)
        """, valores)
    else:
        conn.execute("""
        UPDATE configuracoes
        SET
            nome_empresa = ?,
            login_admin_empresa = ?,
            responsavel_empresa = ?,
            telefone_whatsapp_empresa = ?,
            cidade_uf_empresa = ?,
            observacoes_internas_empresa = ?,
            status_implantacao = ?
        """, valores)

    conn.commit()
    conn.close()

    dados = obter_dados_empresa(fallback_login_admin=login_admin_empresa)
    return True, "Dados da empresa atualizados com sucesso.", dados


def salvar_nome_empresa(nome):
    """Compatibilidade com versões anteriores: salva apenas o nome e preserva os demais campos."""
    dados = obter_dados_empresa()
    ok, _msg, dados_atualizados = salvar_dados_empresa(
        nome,
        dados.get("login_admin_empresa") or _buscar_login_admin_ativo(),
        dados.get("responsavel_empresa", ""),
        dados.get("telefone_whatsapp_empresa", ""),
        dados.get("cidade_uf_empresa", ""),
        dados.get("observacoes_internas_empresa", ""),
        dados.get("status_implantacao", STATUS_IMPLANTACAO_OPCOES[0]),
    )
    if ok and dados_atualizados:
        return dados_atualizados.get("nome_empresa", normalizar_nome_empresa(nome))
    return normalizar_nome_empresa(nome)
