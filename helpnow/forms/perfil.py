import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from flask_login import current_user
from helpnow.models import User

_RE_CPF   = re.compile(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
_RE_PHONE = re.compile(r'^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$')

ESTADOS_BR = [
    ('', 'Selecione o estado'),
    ('AC','AC'),('AL','AL'),('AP','AP'),('AM','AM'),('BA','BA'),
    ('CE','CE'),('DF','DF'),('ES','ES'),('GO','GO'),('MA','MA'),
    ('MT','MT'),('MS','MS'),('MG','MG'),('PA','PA'),('PB','PB'),
    ('PR','PR'),('PE','PE'),('PI','PI'),('RJ','RJ'),('RN','RN'),
    ('RS','RS'),('RO','RO'),('RR','RR'),('SC','SC'),('SP','SP'),
    ('SE','SE'),('TO','TO'),
]


class PerfilForm(FlaskForm):
    # ── Dados pessoais
    name     = StringField('Nome completo',         validators=[DataRequired(), Length(min=3, max=100)])
    email    = EmailField('E-mail',                 validators=[DataRequired(), Email()])
    phone    = StringField('Telefone',              validators=[Optional(), Length(max=20)])
    cpf      = StringField('CPF',                   validators=[Optional(), Length(max=14)])
    photo    = StringField('URL da foto de perfil', validators=[Optional(), Length(max=500)])

    # ── Endereço
    road      = StringField('Rua / Logradouro', validators=[Optional(), Length(max=100)])
    number    = StringField('Número',            validators=[Optional(), Length(max=10)])
    district  = StringField('Bairro',            validators=[Optional(), Length(max=100)])
    zipcode   = StringField('CEP',               validators=[Optional(), Length(max=15)])
    city_name = StringField('Cidade',            validators=[Optional(), Length(max=100)])
    state     = SelectField('Estado', choices=ESTADOS_BR, validators=[Optional()])

    # ── Alteração de senha (opcional — só aplica se preenchida)
    new_password = PasswordField('Nova senha (deixe em branco para manter)', validators=[Optional(), Length(min=6)])
    confirm_pass = PasswordField('Confirmar nova senha', validators=[
                       Optional(), EqualTo('new_password', message='As senhas não conferem.')
                   ])
    submit = SubmitField('Salvar alterações')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user and user.id != current_user.id:
            raise ValidationError('Este e-mail já está em uso por outra conta.')

    def validate_cpf(self, field):
        if field.data and not _RE_CPF.match(field.data):
            raise ValidationError('Formato inválido. Use: 000.000.000-00')

    def validate_phone(self, field):
        if field.data and not _RE_PHONE.match(field.data.strip()):
            raise ValidationError('Formato inválido. Ex: (27) 99999-9999')
