from flask import Flask
from flasgger import Swagger
from config import DevelopmentConfig, ProductionConfig
from extensions import db, migrate, jwt, bcrypt, cors
from routes import users, auth, profile
# from models.token import TokenBlacklist

def create_app(config_class=DevelopmentConfig):
    server =Flask(__name__)

    server.config.from_object(config_class)

    db.init_app(server)
    migrate.init_app(server, db)
    jwt.init_app(server)
    bcrypt.init_app(server)
    cors.init_app(server)

    # @jwt.token_in_blocklist_loader
    # def check_if_token_in_blacklist(jwt_header, jwt_payload):
    #     jti = jwt_payload["jti"]
    #     token = TokenBlacklist.query.filter_by(jti=jti).first()
    #     return token is not None

    server.config['SWAGGER'] = {
        'swagger_version': '2.0',
        'title': 'Growth Momentum API',
        'specs': [
            {
                'version': '0.0.1',
                'title': 'Application',
                'endpoint': 'docs',
                'route': '/api',
                'rule_filter': lambda rule: True
            }
        ],
        'static_url_path': '/api/docs'
    }

    Swagger(server)

    api_prefix = '/api/v1'
    server.register_blueprint(users, url_prefix=api_prefix)
    server.register_blueprint(auth, url_prefix=api_prefix)
    server.register_blueprint(profile, url_prefix=api_prefix)
    @server.route('/', methods=['GET'])
    def index():
        return 'Hello, Welcome to the Growth Momentum API'
    
    return server

if __name__ == "__main__":
    app = create_app(config_class=ProductionConfig if not __debug__ else DevelopmentConfig)
    app.run(host=DevelopmentConfig.HOST, port=DevelopmentConfig.PORT)