from helpnow.views.main   import bp_main
from helpnow.views.auth   import bp_auth
from helpnow.views.perfil import bp_perfil


def init_app(app):
    app.register_blueprint(bp_main)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_perfil)
    app.logger.info("Blueprints registrados: main, auth, perfil")
