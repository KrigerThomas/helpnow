import logging
from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__)

    if app.debug:
        app.logger.setLevel(logging.DEBUG)

    from helpnow.ext.cli import init_app as init_cli
    init_cli(app)

    from helpnow.ext.config import init_app as init_config
    init_config(app)

    if test_config:
        app.config.update(test_config)

    from helpnow.ext.db import init_app as init_db
    init_db(app)

    from helpnow.ext.db import register_models
    register_models()

    if not app.config.get("TESTING"):
        from helpnow.ext.wtf import init_app as init_wtf
        init_wtf(app)

    from helpnow.ext.login import init_app as init_login
    init_login(app)

    from helpnow.ext.debugtoolbar import init_app as init_toolbar
    init_toolbar(app)

    from helpnow.views import init_app as init_site
    init_site(app)

    return app
