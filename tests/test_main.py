import pytest
from helpnow import create_app


# =============================================================================
# FIXTURES (infraestrutura de teste)
# =============================================================================

@pytest.fixture
def app():
    """
    Cria uma instância da aplicação configurada para testes.
    TESTING=True desativa CSRF e usa banco SQLite em memória.
    """
    application = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })

    # Cria todas as tabelas no banco em memória antes de qualquer teste
    with application.app_context():
        from helpnow.ext.db import db
        db.create_all()

    return application

@pytest.fixture
def client(app):
    """
    Cliente HTTP de teste — simula requisições sem servidor real.
    """
    return app.test_client()


# =============================================================================
# TESTES DE INFRAESTRUTURA
# =============================================================================

def test_app_is_created(app):
    """
    Verifica se a aplicação foi criada corretamente.
    """
    assert app is not None


def test_config_is_loaded(app):
    """
    Garante que as configurações de teste foram aplicadas.
    """
    assert app.config["TESTING"] is True


def test_app_runs_in_test_mode(app):
    """
    Confirma explicitamente o modo de execução da aplicação.
    """
    assert app.config["TESTING"] is True


# =============================================================================
# TESTES DE ROTAS
# =============================================================================

def test_rota_inexistente_retorna_404(client):
    """
    Rotas inexistentes devem retornar HTTP 404.
    """
    response = client.get("/rota_que_nao_existe")
    assert response.status_code == 404


ROTAS_PUBLICAS = [
    "/",
    "/buscar",
    "/contato",
    "/auth/login",
    "/auth/cadastro",
]


@pytest.mark.parametrize("rota", ROTAS_PUBLICAS)
def test_rotas_publicas_retornam_200(client, rota):
    """
    Verifica que as rotas públicas do HelpNOW:
    - retornam status HTTP 200
    - entregam HTML válido (DOCTYPE presente)
    """
    response = client.get(rota)
    assert response.status_code == 200, \
        f"Rota {rota} retornou {response.status_code}"
    assert b"<!DOCTYPE html>" in response.data, \
        f"Rota {rota} não retornou HTML válido"


# =============================================================================
# TESTES DE CONTEÚDO
# =============================================================================

def test_landing_page_contem_marca(client):
    """
    Verifica que a landing page exibe a identidade do HelpNOW.
    """
    response = client.get("/")
    assert b"HelpNOW" in response.data


def test_busca_sem_filtro_retorna_pagina(client):
    """
    A página de busca deve carregar mesmo sem resultados no banco.
    """
    response = client.get("/buscar")
    assert response.status_code == 200


def test_busca_com_categoria_retorna_pagina(client):
    """
    A busca filtrada por categoria deve carregar sem erros.
    """
    response = client.get("/buscar?categoria=El%C3%A9trica")
    assert response.status_code == 200


# =============================================================================
# TESTES DE FORMULÁRIO
# =============================================================================

def test_contato_form_valido_redireciona(client):
    """
    Testa o fluxo completo de envio do formulário de contato:
    POST com dados válidos deve redirecionar (302).
    """
    response = client.post(
        "/contato",
        data={
            "nome": "Antony Novais",
            "email": "antony@uvv.br",
            "mensagem": "Mensagem de teste para validação do HelpNOW.",
            "submit": "Enviar Mensagem",
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 302


def test_login_get_retorna_formulario(client):
    """
    A rota de login deve exibir o formulário via GET.
    """
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"E-mail" in response.data


def test_cadastro_get_retorna_formulario(client):
    """
    A rota de cadastro deve exibir o formulário via GET.
    """
    response = client.get("/auth/cadastro")
    assert response.status_code == 200
    assert b"HelpNOW" in response.data


def test_rota_protegida_redireciona_sem_login(client):
    """
    Rotas que exigem autenticação devem redirecionar para login
    quando o usuário não está autenticado.
    """
    response = client.get("/perfil/")
    assert response.status_code == 302
    assert "/auth/login" in response.headers.get("Location", "")
