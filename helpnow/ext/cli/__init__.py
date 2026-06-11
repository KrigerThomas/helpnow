import click
from flask import current_app
from helpnow.ext.db import db
from helpnow.models import *


def init_app(app):

    @app.cli.command("create-db")
    def create_db():
        """Cria todas as tabelas do banco de dados."""
        db.create_all()
        click.echo("Banco de dados criado com sucesso!")

    @app.cli.command("drop-db")
    @click.confirmation_option(prompt="Tem certeza que deseja apagar TUDO?")
    def drop_db():
        db.drop_all()
        click.echo("Banco de dados removido.")

    @app.cli.command("seed-dev")
    def seed_dev():
        """Popula o banco com cenário completo para desenvolvimento."""
        is_dev = (
            app.config.get("ENV") == "development"
            or app.debug is True
            or current_app.config.get("FLASK_ENV") == "development"
        )
        if not is_dev:
            raise click.ClickException("BLOQUEADO: apenas em ambiente de desenvolvimento.")

        click.echo("Isso irá recriar o banco e popular com dados de teste. Continuar? [y/N]: ", nl=False)
        if input().strip().lower() not in ("y", "yes", "s", "sim"):
            click.echo("Cancelado.")
            return

        try:
            click.echo("Limpando banco...")
            db.drop_all()
            db.create_all()

            # ── Papéis ──────────────────────────────────────────────────────
            role_cliente   = Role(name="Cliente")
            role_prestador = Role(name="Prestador")
            db.session.add_all([role_cliente, role_prestador])
            db.session.flush()

            # ── Cidade ──────────────────────────────────────────────────────
            vila_velha = City(name="Vila Velha", state="ES", country="Brasil", region="Sudeste")
            db.session.add(vila_velha)
            db.session.flush()

            # ── Cliente: Thomas ───────────────────────────────────────────────
            thomas = User(
                name="Thomás Kriger",
                email="thomas@email.com",
                cpf="444.444.444-44",
                phone="(27) 99999-1111",
                is_active=True,
                photo="https://i.postimg.cc/MG594v8j/Whats-App-Image-2026-06-04-at-1-25-47-AM.jpg",
            )
            thomas.set_password("123456")
            thomas.addresses.append(
                Address(road="Avenida Champagnat", number="925",
                        district="Praia da Costa", zipcode="29146-010", city=vila_velha)
            )
            thomas.role_associations.append(RoleUser(role=role_cliente))
            db.session.add(thomas)

            # ── Prestador: Heitor ────────────────────────────────────────────
            heitor = User(
                name="Heitor Eletricista",
                email="heitor@email.com",
                cpf="555.555.555-55",
                phone="(27) 99999-2222",
                is_active=True,
                photo="https://media.gettyimages.com/id/2061516149/pt/foto/man-portrait-and-safety-goggles-for-engineer-in-workshop-construction-or-maintenance-with.jpg?s=612x612&w=gi&k=20&c=O0iqLbAVLAmUUKvgRT0bgU2vVGbR7KH5iLO-DOlV_2Y="
            )
            heitor.set_password("123456")
            heitor.addresses.append(
                Address(road="Rua das Palmeiras", number=100,
                        district="Itapuã", zipcode="29101-000", city=vila_velha)
            )
            heitor.role_associations.append(RoleUser(role=role_prestador))
            db.session.add(heitor)

            # ── Prestador: Antony ──────────────────────────────────────────────
            antony = User(
                name="Antony Informática",
                email="antony@email.com",
                cpf="666.666.666-66",
                phone="(27) 99999-3333",
                is_active=True,
                photo="https://cdn.sistemawbuy.com.br/arquivos/6cb118ca80ea7a87a37687679949a415/produtos/690e7e5c52a37/design-sem-nome-21-6911deb107caf.jpg"
            )
            antony.set_password("123456")
            antony.addresses.append(
                Address(road="Av. Est. José Júlio de Souza", number=3030,
                        district="Itaparica", zipcode="29101-000", city=vila_velha)
            )
            antony.role_associations.append(RoleUser(role=role_prestador))
            db.session.add(antony)
            db.session.flush()

            # ── Serviços ─────────────────────────────────────────────────────
            servicos_heitor = [
                Servico(titulo="Instalação elétrica residencial",
                        categoria="Elétrica",
                        descricao="Instalação e manutenção de tomadas, disjuntores e fiação.",
                        preco=150.00, localidade="Vila Velha, ES", prestador_id=heitor.id),
                Servico(titulo="Reparo de curto-circuito",
                        categoria="Elétrica",
                        descricao="Diagnóstico e conserto de curto-circuitos residenciais.",
                        preco=80.00, localidade="Vila Velha, ES", prestador_id=heitor.id),
            ]
            servico_antony = Servico(
                titulo="Manutenção de computadores",
                categoria="Informática",
                descricao="Diagnóstico e reparo de problemas em computadores.",
                preco=120.00, localidade="Vila Velha, ES", prestador_id=antony.id,
            )
            db.session.add_all(servicos_heitor + [servico_antony])
            db.session.flush()

            # ── Solicitação pendente ──────────────────────────────────────────
            sol = Solicitacao(
                cliente_id=thomas.id,
                servico_id=servicos_heitor[0].id,
                mensagem="Preciso instalar 6 tomadas novas no meu quarto.",
                endereco_texto="R. Inácio Higino, 1170 – Praia da Costa",
            )
            db.session.add(sol)

            # ── Solicitação concluída com avaliação (demonstra histórico) ─────
            sol_concluida = Solicitacao(
                cliente_id=thomas.id,
                servico_id=servico_antony.id,
                mensagem="Preciso de uma limpeza aqui no meu PC, ele está muito lento.",
                endereco_texto="R. Inácio Higino, 1170 – Praia da Costa",
                status=STATUS_CONCLUIDO,
                nota=5,
            )
            db.session.add(sol_concluida)
            db.session.commit()

            click.echo("")
            click.echo("✓ Seed concluído! Contas (senha: 123456):")
            click.echo("  Cliente    → thomas@email.com")
            click.echo("  Prestador  → heitor@email.com")
            click.echo("  Prestador → antony@email.com")

        except Exception as e:
            db.session.rollback()
            click.echo(f"Erro no seed: {e}")
            raise
