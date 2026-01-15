import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-desenvolvimento'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurações da empresa (podem ser alteradas)
    EMPRESA_NOME = 'Minha Empresa'
    EMPRESA_CNPJ = ''
    EMPRESA_ENDERECO = ''
    EMPRESA_TELEFONE = ''
    EMPRESA_EMAIL = ''
