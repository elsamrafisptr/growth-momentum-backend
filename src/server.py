from flasgger import Swagger
from flask import Flask
from flask.blueprints import Blueprint

import config
import routes
# from models import db

server = Flask(__name__)

@server.route('/')
def index():
    return 'Hello Elsam Rafi Saputra and Eny Lowti'


server.config["SWAGGER"] = {
    "swagger_version": "2.0",
    "title": "Application",
    "specs": [
        {
            "version": "0.0.1",
            "title": "Application",
            "endpoint": "spec",
            "route": "/application/spec",
            "rule_filter": lambda rule: True,  # all in
        }
    ],
    "static_url_path": "/apidocs",
}

Swagger(server)

server.debug = config.DEBUG
# server.config["SQLALCHEMY_DATABASE_URI"] = config.DB_URI
# server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS
# db.init_app(server)
# db.app = server

for blueprint in vars(routes).values():
    if isinstance(blueprint, Blueprint):
        server.register_blueprint(blueprint, url_prefix=config.APPLICATION_ROOT)

if __name__ == "__main__":
    server.run(host=config.HOST, port=config.PORT, debug=True)