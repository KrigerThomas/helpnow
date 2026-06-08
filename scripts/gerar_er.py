"""
Gera o diagrama ER do HelpNOW usando graphviz.
"""

import graphviz

# ── Paleta ────────────────────────────────────────────────────────────────────
COR_CABECALHO = "#1E3C64"
COR_TXT_CAB   = "white"
COR_FUNDO     = "#F8F8F8"
COR_BORDA     = "#4A4A4A"
COR_FK        = "#777777"
COR_PK        = "#1E3C64"
FONTE         = "Helvetica"

# ── Definição das tabelas ─────────────────────────────────────────────────────
TABELAS = {
    "users": [
        ("id",         "INTEGER",      "PK"),
        ("name",       "VARCHAR(100)", "NN IDX"),
        ("email",      "VARCHAR(100)", "UQ NN"),
        ("password",   "VARCHAR(255)", ""),
        ("phone",      "VARCHAR(20)",  ""),
        ("cpf",        "VARCHAR(14)",  "UQ IDX"),
        ("photo",      "VARCHAR(500)", ""),
        ("is_active",  "BOOLEAN",      "NN"),
        ("created_at", "DATETIME",     "NN"),
        ("updated_at", "DATETIME",     ""),
    ],
    "roles": [
        ("id",     "INTEGER",     "PK"),
        ("name",   "VARCHAR(30)", "UQ IDX"),
        ("status", "BOOLEAN",     "NN"),
    ],
    "roles_has_users": [
        ("id",          "INTEGER",  "PK"),
        ("role_id",     "INTEGER",  "FK"),
        ("user_id",     "INTEGER",  "FK"),
        ("created_at",  "DATETIME", "NN"),
        ("finished_at", "DATETIME", ""),
    ],
    "cities": [
        ("id",      "INTEGER",      "PK"),
        ("name",    "VARCHAR(100)", "NN"),
        ("state",   "VARCHAR(2)",   ""),
        ("country", "VARCHAR(50)",  ""),
        ("region",  "VARCHAR(50)",  ""),
    ],
    "address": [
        ("id",       "INTEGER",      "PK"),
        ("road",     "VARCHAR(100)", ""),
        ("number",   "VARCHAR(15)",  ""),
        ("district", "VARCHAR(100)", ""),
        ("zipcode",  "VARCHAR(15)",  ""),
        ("user_id",  "INTEGER",      "FK"),
        ("city_id",  "INTEGER",      "FK"),
    ],
    "servicos": [
        ("id",           "INTEGER",      "PK"),
        ("titulo",       "VARCHAR(120)", "NN"),
        ("descricao",    "TEXT",         ""),
        ("categoria",    "VARCHAR(60)",  "NN IDX"),
        ("preco",        "FLOAT",        ""),
        ("localidade",   "VARCHAR(100)", ""),
        ("ativo",        "BOOLEAN",      "NN"),
        ("created_at",   "DATETIME",     "NN"),
        ("prestador_id", "INTEGER",      "FK"),
    ],
    "solicitacoes": [
        ("id",             "INTEGER",      "PK"),
        ("status",         "VARCHAR(20)",  "NN IDX"),
        ("mensagem",       "TEXT",         ""),
        ("endereco_texto", "VARCHAR(200)", ""),
        ("nota",           "INTEGER",      ""),
        ("created_at",     "DATETIME",     "NN"),
        ("updated_at",     "DATETIME",     ""),
        ("cliente_id",     "INTEGER",      "FK"),
        ("servico_id",     "INTEGER",      "FK"),
    ],
}

# ── Relacionamentos ───────────────────────────────────────────────────────────
RELACOES = [
    ("users",    "roles_has_users", "",            "1", "N"),
    ("roles",    "roles_has_users", "",            "1", "N"),
    ("users",    "address",         "CASCADE DEL", "1", "N"),
    ("cities",   "address",         "SET NULL",    "1", "N"),
    ("users",    "servicos",        "prestador",   "1", "N"),
    ("users",    "solicitacoes",    "cliente",     "1", "N"),
    ("servicos", "solicitacoes",    "",            "1", "N"),
]


def linha_tabela(col, tipo, flags):
    eh_pk = "PK" in flags
    eh_fk = "FK" in flags

    if eh_pk:
        icone   = u"\U0001F511 "   # 🔑
        cor_col = COR_PK
        peso    = "b"
    elif eh_fk:
        icone   = u"\U0001F517 "   # 🔗
        cor_col = COR_FK
        peso    = ""
    else:
        icone   = "      "
        cor_col = "#222222"
        peso    = ""

    badges = []
    for f in ["PK", "UQ", "NN", "IDX"]:
        if f in flags:
            badges.append(f)
    badge_str = "  ".join(
        f'<FONT COLOR="#aaaaaa" POINT-SIZE="8">[{b}]</FONT>' for b in badges
    )

    col_disp  = f"<{peso}>{col}</{peso}>" if peso else col
    tipo_disp = f'<FONT COLOR="#aaaaaa" POINT-SIZE="9"> {tipo}</FONT>'

    return (
        f'<TR>'
        f'<TD ALIGN="LEFT" BALIGN="LEFT" BORDER="0" CELLPADDING="4">'
        f'<FONT COLOR="{cor_col}" FACE="{FONTE}" POINT-SIZE="11">'
        f'{icone}{col_disp}'
        f'</FONT>'
        f'{tipo_disp} {badge_str}'
        f'</TD>'
        f'</TR>'
    )


def montar_label(nome, colunas):
    cabecalho = (
        f'<TR>'
        f'<TD BGCOLOR="{COR_CABECALHO}" ALIGN="CENTER" BORDER="0" CELLPADDING="7">'
        f'<FONT COLOR="{COR_TXT_CAB}" FACE="{FONTE}" POINT-SIZE="13"><B>{nome}</B></FONT>'
        f'</TD>'
        f'</TR>'
    )
    linhas = "\n".join(linha_tabela(c, t, f) for c, t, f in colunas)
    return (
        f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="2" '
        f'BGCOLOR="{COR_FUNDO}" COLOR="{COR_BORDA}">\n'
        f'{cabecalho}\n{linhas}\n</TABLE>>'
    )


# ── Grafo ─────────────────────────────────────────────────────────────────────
dot = graphviz.Digraph(name="HelpNOW_ER", format="png")

dot.attr(
    rankdir="LR",
    splines="polyline",
    nodesep="0.9",
    ranksep="1.8",
    bgcolor="white",
    fontname=FONTE,
    pad="0.7",
    dpi="200",
)
dot.attr("node", shape="none", margin="0", fontname=FONTE)
dot.attr("edge",
    fontname=FONTE,
    fontsize="11",
    color="#555555",
    arrowsize="0.9",
    penwidth="1.2",
)

# Nós
for tabela, colunas in TABELAS.items():
    dot.node(tabela, label=montar_label(tabela, colunas))

# Arestas
for orig, dest, lbl, tail, head in RELACOES:
    dot.edge(
        orig, dest,
        xlabel=f" {lbl}" if lbl else "",
        taillabel=tail,
        headlabel=head,
        arrowhead="crow",
        arrowtail="none",
        dir="both",
        labeldistance="2.0",
        labelangle="30",
        fontcolor="#555555",
        color="#555555",
    )

# ── Saída ─────────────────────────────────────────────────────────────────────
saida = "er_diagram"
dot.render(saida, cleanup=True)
print(f"Diagrama gerado: {saida}.png")