import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, EmailField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
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


class LoginForm(FlaskForm):
    email    = EmailField('E-mail',  validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    lembrar  = BooleanField('Lembrar de mim')
    submit   = SubmitField('Entrar')


class CadastroForm(FlaskForm):
    # ── Dados básicos (todos os usuários)
    name  = StringField('Nome completo', validators=[DataRequired(), Length(min=3, max=100)])
    email = EmailField('E-mail',         validators=[DataRequired(), Email()])
    phone = StringField('Telefone',      validators=[Optional(), Length(max=20)])
    papel = SelectField('Tipo de conta', choices=[
                ('cliente',   'Cliente – preciso de serviços'),
                ('prestador', 'Prestador – ofereço serviços'),
            ], validators=[DataRequired()])

    # ── Dados extras
    # SEM Optional() nos campos condicionais.
    # Optional() interrompe toda a validação do campo quando vazio,
    # impedindo que validate_cpf() seja chamado. Sem ele, o método
    # customizado sempre executa e decide sozinho o que exigir.
    cpf   = StringField('CPF',                  validators=[Length(max=14)])
    photo = StringField('URL da foto de perfil', validators=[Optional(), Length(max=500)])

    # ── Endereço
    # Mesmo motivo: sem Optional() em road, city_name e state.
    # number, district e zipcode são genuinamente opcionais para qualquer papel.
    road      = StringField('Rua / Logradouro', validators=[Length(max=100)])
    number    = StringField('Número',           validators=[Optional(), Length(max=10)])
    district  = StringField('Bairro',           validators=[Optional(), Length(max=100)])
    zipcode   = StringField('CEP',              validators=[Optional(), Length(max=15)])
    city_name = StringField('Cidade',           validators=[Length(max=100)])
    state     = SelectField('Estado', choices=ESTADOS_BR)

    # ── Senha
    password = PasswordField('Senha',          validators=[DataRequired(), Length(min=6)])
    confirm  = PasswordField('Confirmar senha', validators=[
                   DataRequired(), EqualTo('password', message='As senhas não conferem.')
               ])
    submit = SubmitField('Criar conta')

    # ── Validadores customizados ──────────────────────────────────────────────
    # Chamados pelo WTForms automaticamente para cada campo (validate_<campo>).
    # Agora que removemos Optional(), estes métodos sempre executam.

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Este e-mail já está cadastrado.')

    def validate_cpf(self, field):
        if self.papel.data == 'prestador':
            if not field.data or not field.data.strip():
                raise ValidationError('CPF é obrigatório para prestadores.')
            if not _RE_CPF.match(field.data.strip()):
                raise ValidationError('Formato inválido. Use: 000.000.000-00')
        elif field.data and field.data.strip():
            # Cliente preencheu — valida o formato mesmo assim
            if not _RE_CPF.match(field.data.strip()):
                raise ValidationError('Formato inválido. Use: 000.000.000-00')

    def validate_phone(self, field):
        if field.data and field.data.strip():
            if not _RE_PHONE.match(field.data.strip()):
                raise ValidationError('Formato inválido. Ex: (27) 99999-9999')

    def validate_road(self, field):
        if self.papel.data == 'prestador':
            if not field.data or not field.data.strip():
                raise ValidationError('Endereço é obrigatório para prestadores.')

    def validate_city_name(self, field):
        if self.papel.data == 'prestador':
            if not field.data or not field.data.strip():
                raise ValidationError('Cidade é obrigatória para prestadores.')

    def validate_state(self, field):
        if self.papel.data == 'prestador':
            if not field.data or field.data.strip() == '':
                raise ValidationError('Estado é obrigatório para prestadores.')
