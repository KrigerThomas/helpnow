from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from sqlalchemy import func
from helpnow.ext.db import db
from helpnow.models import Servico, Solicitacao
from helpnow.models import STATUS_PENDENTE, STATUS_ACEITO, STATUS_RECUSADO, STATUS_CONCLUIDO
from helpnow.forms.main import ContatoForm

bp_main = Blueprint("main", __name__)

CATEGORIAS = ["Elétrica", "Hidráulica", "Limpeza", "Informática", "Pintura", "Outros"]


def _exige_papel(papel_requerido: str):
    if not current_user.is_authenticated:
        flash("Faça login para continuar.", "warning")
        return redirect(url_for("auth.login"))
    if current_user.papel != papel_requerido:
        flash("Acesso não permitido para este tipo de conta.", "danger")
        return redirect(url_for("main.index"))
    return None


def _calcular_avaliacao_media(prestador_id: int):
    """
    Calcula a média real das notas recebidas pelo prestador.
    Retorna float arredondado em 1 casa, ou None se não houver avaliações.
    """
    resultado = (
        db.session.query(func.avg(Solicitacao.nota))
        .join(Servico, Solicitacao.servico_id == Servico.id)
        .filter(
            Servico.prestador_id == prestador_id,
            Solicitacao.nota.isnot(None),
        )
        .scalar()
    )
    return round(float(resultado), 1) if resultado else None


# ── ROTAS PÚBLICAS ────────────────────────────────────────────────────────────

@bp_main.route("/")
@bp_main.route("/index")
def index():
    if not current_user.is_authenticated:
        return render_template("main/index.html")

    user = current_user

    if user.papel == "prestador":
        meus_servicos = Servico.query.filter_by(prestador_id=user.id, ativo=True).all()

        sol_pendentes = (Solicitacao.query
                         .join(Servico)
                         .filter(Servico.prestador_id == user.id,
                                 Solicitacao.status == STATUS_PENDENTE)
                         .order_by(Solicitacao.created_at.desc()).all())

        aceitos_mes = (Solicitacao.query
                       .join(Servico)
                       .filter(Servico.prestador_id == user.id,
                               Solicitacao.status == STATUS_ACEITO)
                       .count())

        # Histórico: concluídas e recusadas
        sol_historico = (Solicitacao.query
                         .join(Servico)
                         .filter(Servico.prestador_id == user.id,
                                 Solicitacao.status.in_([STATUS_ACEITO,
                                                         STATUS_RECUSADO,
                                                         STATUS_CONCLUIDO]))
                         .order_by(Solicitacao.created_at.desc())
                         .limit(20).all())

        # Avaliação média REAL calculada do banco
        avaliacao_media = _calcular_avaliacao_media(user.id)

        return render_template(
            "main/index_prestador.html",
            user=user,
            enderecos=user.addresses,
            solicitacoes=sol_pendentes,
            sol_historico=sol_historico,
            servicos=meus_servicos,
            solicitacoes_pendentes=len(sol_pendentes),
            aceitos_mes=aceitos_mes,
            avaliacao_media=avaliacao_media,
            total_servicos=len(meus_servicos),
        )
    else:
        todas = (Solicitacao.query
                 .filter_by(cliente_id=user.id)
                 .order_by(Solicitacao.created_at.desc()).all())
        sol_ativas    = [s for s in todas if s.status in (STATUS_PENDENTE, STATUS_ACEITO)]
        sol_historico = [s for s in todas if s.status in (STATUS_RECUSADO, STATUS_CONCLUIDO)]

        return render_template(
            "main/index_cliente.html",
            user=user,
            enderecos=user.addresses,
            sol_ativas=sol_ativas,
            sol_historico=sol_historico,
        )


@bp_main.route("/buscar")
def buscar():
    categoria  = request.args.get("categoria", "")
    localidade = request.args.get("localidade", "")
    q = Servico.query.filter_by(ativo=True)
    if categoria:
        q = q.filter(Servico.categoria == categoria)
    if localidade:
        q = q.filter(Servico.localidade.ilike(f"%{localidade}%"))
    return render_template(
        "main/buscar.html",
        categorias=CATEGORIAS,
        categoria=categoria,
        localidade=localidade,
        resultados=q.order_by(Servico.created_at.desc()).all(),
    )


@bp_main.route("/contato", methods=["GET", "POST"])
def contato():
    form = ContatoForm()
    if form.validate_on_submit():
        flash("Mensagem enviada com sucesso!", "success")
        return redirect(url_for("main.index"))
    return render_template("main/contato.html", form=form)


# ── ROTAS DO PRESTADOR ────────────────────────────────────────────────────────

@bp_main.route("/servico/novo", methods=["GET", "POST"])
@login_required
def novo_servico():
    redir = _exige_papel("prestador")
    if redir:
        return redir
    from helpnow.forms.servico import ServicoForm
    form = ServicoForm()
    if form.validate_on_submit():
        s = Servico(
            titulo=form.titulo.data,
            categoria=form.categoria.data,
            descricao=form.descricao.data,
            preco=float(form.preco.data) if form.preco.data else None,
            localidade=form.localidade.data,
            prestador_id=current_user.id,
        )
        db.session.add(s)
        db.session.commit()
        flash("Serviço cadastrado com sucesso!", "success")
        return redirect(url_for("main.index"))
    return render_template("main/novo_servico.html", form=form)


@bp_main.route("/servico/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar_servico(id):
    redir = _exige_papel("prestador")
    if redir:
        return redir

    servico = db.get_or_404(Servico, id)

    if servico.prestador_id != current_user.id:
        flash("Você não tem permissão para editar este serviço.", "danger")
        return redirect(url_for("main.index"))

    from helpnow.forms.servico import ServicoForm
    # obj= pré-popula o WTForms com os dados do modelo
    form = ServicoForm(obj=servico)

    if form.validate_on_submit():
        servico.titulo    = form.titulo.data
        servico.categoria = form.categoria.data
        servico.descricao = form.descricao.data
        servico.preco     = float(form.preco.data) if form.preco.data else None
        servico.localidade = form.localidade.data
        db.session.commit()
        flash("Serviço atualizado com sucesso!", "success")
        return redirect(url_for("main.index"))

    return render_template("main/editar_servico.html", form=form, servico=servico)


@bp_main.route("/servico/<int:id>/desativar", methods=["POST"])
@login_required
def desativar_servico(id):
    redir = _exige_papel("prestador")
    if redir:
        return redir
    servico = db.get_or_404(Servico, id)
    if servico.prestador_id != current_user.id:
        flash("Você não tem permissão.", "danger")
        return redirect(url_for("main.index"))
    servico.ativo = False
    db.session.commit()
    flash(f'Serviço "{servico.titulo}" removido da listagem.', "info")
    return redirect(url_for("main.index"))


@bp_main.route("/solicitacao/<int:id>/aceitar", methods=["POST"])
@login_required
def aceitar_solicitacao(id):
    redir = _exige_papel("prestador")
    if redir:
        return redir
    sol = db.get_or_404(Solicitacao, id)
    sol.status = STATUS_ACEITO
    db.session.commit()
    flash("Solicitação aceita!", "success")
    return redirect(url_for("main.index"))


@bp_main.route("/solicitacao/<int:id>/recusar", methods=["POST"])
@login_required
def recusar_solicitacao(id):
    redir = _exige_papel("prestador")
    if redir:
        return redir
    sol = db.get_or_404(Solicitacao, id)
    sol.status = STATUS_RECUSADO
    db.session.commit()
    flash("Solicitação recusada.", "info")
    return redirect(url_for("main.index"))


# ── ROTAS DO CLIENTE ──────────────────────────────────────────────────────────

@bp_main.route("/solicitar/<int:servico_id>", methods=["GET", "POST"])
@login_required
def solicitar(servico_id):
    redir = _exige_papel("cliente")
    if redir:
        return redir
    from helpnow.forms.servico import SolicitacaoForm
    servico = db.get_or_404(Servico, servico_id)
    form    = SolicitacaoForm()
    if form.validate_on_submit():
        sol = Solicitacao(
            cliente_id=current_user.id,
            servico_id=servico.id,
            mensagem=form.mensagem.data,
            endereco_texto=form.endereco_texto.data,
        )
        db.session.add(sol)
        db.session.commit()
        flash("Solicitação enviada! Aguarde o retorno do prestador.", "success")
        return redirect(url_for("main.index"))
    return render_template("main/solicitar.html", servico=servico, form=form)


@bp_main.route("/solicitacao/<int:id>/concluir", methods=["POST"])
@login_required
def concluir_solicitacao(id):
    redir = _exige_papel("cliente")
    if redir:
        return redir
    sol = db.get_or_404(Solicitacao, id)
    if sol.cliente_id != current_user.id or sol.status != STATUS_ACEITO:
        flash("Ação não permitida.", "danger")
        return redirect(url_for("main.index"))
    nota_raw = request.form.get("nota")
    sol.status = STATUS_CONCLUIDO
    if nota_raw and nota_raw.isdigit():
        sol.nota = max(1, min(5, int(nota_raw)))
    db.session.commit()
    flash("Serviço concluído. Obrigado pela avaliação!", "success")
    return redirect(url_for("main.index"))
