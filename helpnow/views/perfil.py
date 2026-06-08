from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from helpnow.ext.db import db
from helpnow.models import Address, City

bp_perfil = Blueprint("perfil", __name__, url_prefix="/perfil")


@bp_perfil.route("/", methods=["GET", "POST"])
@login_required
def index():
    from helpnow.forms.perfil import PerfilForm

    user = current_user
    addr = user.endereco_principal

    form = PerfilForm(
        name=user.name,
        email=user.email,
        phone=user.phone or "",
        cpf=user.cpf or "",
        photo=user.photo or "",
        road=addr.road         if addr else "",
        number=addr.number     if addr and addr.number else "",  # já é String
        district=addr.district if addr else "",
        zipcode=addr.zipcode   if addr else "",
        city_name=addr.city.name if addr and addr.city else "",
        state=addr.city.state    if addr and addr.city else "",
    )

    if form.validate_on_submit():
        user.name  = form.name.data.strip()
        user.email = form.email.data.strip().lower()
        user.phone = form.phone.data.strip() if form.phone.data else None
        user.cpf   = form.cpf.data.strip()   if form.cpf.data   else None
        user.photo = form.photo.data.strip()  if form.photo.data else None

        if form.new_password.data:
            user.set_password(form.new_password.data)

        if form.road.data and form.road.data.strip():
            city = None
            if form.city_name.data and form.city_name.data.strip():
                city = City.query.filter_by(
                    name=form.city_name.data.strip(),
                    state=form.state.data or None
                ).first()
                if not city:
                    city = City(
                        name=form.city_name.data.strip(),
                        state=form.state.data or None,
                        country="Brasil",
                    )
                    db.session.add(city)
                    db.session.flush()

            if addr:
                addr.road     = form.road.data.strip()
                addr.number   = form.number.data.strip() if form.number.data else None
                addr.district = form.district.data.strip() if form.district.data else None
                addr.zipcode  = form.zipcode.data.strip()  if form.zipcode.data  else None
                addr.city     = city
            else:
                new_addr = Address(
                    road=form.road.data.strip(),
                    number=form.number.data.strip() if form.number.data else None,
                    district=form.district.data.strip() if form.district.data else None,
                    zipcode=form.zipcode.data.strip()   if form.zipcode.data   else None,
                    city=city,
                )
                user.addresses.append(new_addr)

        db.session.commit()
        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for("perfil.index"))

    return render_template("main/perfil.html", form=form, user=user, addr=addr)
