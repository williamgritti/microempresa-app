from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # Registrar blueprints
    from app.routes.main import main_bp
    from app.routes.clientes import clientes_bp
    from app.routes.produtos import produtos_bp
    from app.routes.financeiro import financeiro_bp
    from app.routes.orcamentos import orcamentos_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    app.register_blueprint(produtos_bp, url_prefix='/produtos')
    app.register_blueprint(financeiro_bp, url_prefix='/financeiro')
    app.register_blueprint(orcamentos_bp, url_prefix='/orcamentos')

    # Criar tabelas do banco
    with app.app_context():
        db.create_all()

    return app
