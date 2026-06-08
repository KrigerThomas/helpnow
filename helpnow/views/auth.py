from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from helpnow.ext.db import db
from helpnow.models import User, Role, RoleUser, Address, City

bp_auth = Blueprint("auth", __name__, url_prefix="/auth")


@bp_auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    from helpnow.forms.auth import LoginForm
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.lembrar.data)
            flash(f"Bem-vindo, {user.name.split()[0]}!", "success")
            return redirect(request.args.get("next") or url_for("main.index"))
        flash("E-mail ou senha incorretos.", "danger")

    return render_template("main/login.html", form=form)


@bp_auth.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    from helpnow.forms.auth import CadastroForm
    form = CadastroForm()

    if form.validate_on_submit():
        # ── Papel ──────────────────────────────────────────────────────────
        nome_papel = "Prestador" if form.papel.data == "prestador" else "Cliente"
        role = Role.query.filter_by(name=nome_papel).first()
        if not role:
            role = Role(name=nome_papel)
            db.session.add(role)
            db.session.flush()

        # ── Usuário ────────────────────────────────────────────────────────
        user = User(
            name=form.name.data.strip(),
            email=form.email.data.strip().lower(),
            phone=form.phone.data.strip() if form.phone.data else None,
            cpf=form.cpf.data.strip()     if form.cpf.data   else None,
            photo=form.photo.data.strip() if form.photo.data else None,
        )
        user.set_password(form.password.data)
        user.role_associations.append(RoleUser(role=role))

        # ── Endereço (salvo para qualquer um que preencher a rua) ──────────
        if form.road.data and form.road.data.strip():
            city = None
            if form.city_name.data and form.city_name.data.strip():
                city = City.query.filter_by(
                    name=form.city_name.data.strip(),
                    state=form.state.data or None,
                ).first()
                if not city:
                    city = City(
                        name=form.city_name.data.strip(),
                        state=form.state.data or None,
                        country="Brasil",
                    )
                    db.session.add(city)
                    db.session.flush()

            addr = Address(
                road=form.road.data.strip(),
                # number agora é String no modelo — passa direto, sem int()
                number=form.number.data.strip() if form.number.data else None,
                district=form.district.data.strip() if form.district.data else None,
                zipcode=form.zipcode.data.strip()   if form.zipcode.data   else None,
                city=city,
            )
            user.addresses.append(addr)

        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f"Conta criada! Bem-vindo, {user.name.split()[0]}!", "success")
        return redirect(url_for("main.index"))

    return render_template("main/cadastro.html", form=form)


@bp_auth.route("/logout")
@login_required
def logout():
    flash(f"Até logo, {current_user.name.split()[0]}!", "info")
    logout_user()
    return redirect(url_for("main.index"))
