from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ServicoForm(FlaskForm):
    titulo    = StringField('Título do serviço',
                    validators=[DataRequired(), Length(min=5, max=120)])
    categoria = SelectField('Categoria', choices=[
                    ('Elétrica',    'Elétrica'),
                    ('Hidráulica',  'Hidráulica'),
                    ('Limpeza',     'Limpeza / Diarista'),
                    ('Informática', 'Informática'),
                    ('Pintura',     'Pintura'),
                    ('Outros',      'Outros'),
                ], validators=[DataRequired()])
    descricao  = TextAreaField('Descrição',
                    validators=[DataRequired(), Length(min=10)])
    # "Preço fixo" — valor único cobrado pelo serviço
    preco      = DecimalField('Preço fixo (R$)',
                    validators=[Optional(), NumberRange(min=0)], places=2)
    localidade = StringField('Localidade (cidade/bairro)',
                    validators=[Optional(), Length(max=100)])
    submit     = SubmitField('Salvar serviço')


class SolicitacaoForm(FlaskForm):
    mensagem       = TextAreaField('Descreva o que precisa',
                         validators=[DataRequired(), Length(min=10)])
    endereco_texto = StringField('Endereço para atendimento',
                         validators=[DataRequired(), Length(min=5, max=200)])
    submit         = SubmitField('Solicitar serviço')
