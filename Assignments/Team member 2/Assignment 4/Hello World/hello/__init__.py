from flask import Flask

def create_app():
    app = Flask(__name__)

    # registering the blue print with the app
    from .views import blue_print
    app.register_blueprint(blueprint=blue_print, appendix='/')

    return app