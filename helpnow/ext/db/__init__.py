from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)

def register_models():
    """
    Registra todos os modelos do HelpNOW no metadata do SQLAlchemy.
    """
    import helpnow.models.role
    import helpnow.models.user
    import helpnow.models.role_user
    import helpnow.models.location
    import helpnow.models.servico
    import helpnow.models.solicitacao
