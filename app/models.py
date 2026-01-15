from datetime import datetime
from app import db


class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    documento = db.Column(db.String(18), unique=True)  # CPF ou CNPJ
    tipo_documento = db.Column(db.String(4), default='CPF')  # CPF ou CNPJ
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    cep = db.Column(db.String(10))
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    orcamentos = db.relationship('Orcamento', backref='cliente', lazy=True)
    movimentacoes = db.relationship('Movimentacao', backref='cliente', lazy=True)

    def __repr__(self):
        return f'<Cliente {self.nome}>'


class Produto(db.Model):
    __tablename__ = 'produtos'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    categoria = db.Column(db.String(50))
    unidade = db.Column(db.String(10), default='UN')  # UN, KG, L, M, etc.
    preco_custo = db.Column(db.Float, default=0)
    preco_venda = db.Column(db.Float, default=0)
    quantidade = db.Column(db.Float, default=0)
    estoque_minimo = db.Column(db.Float, default=0)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    movimentacoes_estoque = db.relationship('MovimentacaoEstoque', backref='produto', lazy=True)
    itens_orcamento = db.relationship('ItemOrcamento', backref='produto', lazy=True)

    def __repr__(self):
        return f'<Produto {self.nome}>'

    @property
    def estoque_baixo(self):
        return self.quantidade <= self.estoque_minimo

    @property
    def margem_lucro(self):
        if self.preco_custo > 0:
            return ((self.preco_venda - self.preco_custo) / self.preco_custo) * 100
        return 0


class MovimentacaoEstoque(db.Model):
    __tablename__ = 'movimentacoes_estoque'

    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # entrada ou saida
    quantidade = db.Column(db.Float, nullable=False)
    motivo = db.Column(db.String(200))
    data = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MovimentacaoEstoque {self.tipo} {self.quantidade}>'


class Movimentacao(db.Model):
    __tablename__ = 'movimentacoes'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), nullable=False)  # entrada ou saida
    valor = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(50))
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    data_vencimento = db.Column(db.Date)
    pago = db.Column(db.Boolean, default=True)
    forma_pagamento = db.Column(db.String(50))
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    orcamento_id = db.Column(db.Integer, db.ForeignKey('orcamentos.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Movimentacao {self.tipo} R${self.valor:.2f}>'


class Orcamento(db.Model):
    __tablename__ = 'orcamentos'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    data = db.Column(db.Date, default=datetime.utcnow)
    validade = db.Column(db.Date)
    status = db.Column(db.String(20), default='pendente')  # pendente, aprovado, recusado, concluido
    observacoes = db.Column(db.Text)
    desconto = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    itens = db.relationship('ItemOrcamento', backref='orcamento', lazy=True, cascade='all, delete-orphan')
    movimentacoes = db.relationship('Movimentacao', backref='orcamento', lazy=True)

    def __repr__(self):
        return f'<Orcamento {self.numero}>'

    @property
    def subtotal(self):
        return sum(item.total for item in self.itens)

    @property
    def total(self):
        return self.subtotal - self.desconto

    @staticmethod
    def gerar_numero():
        ultimo = Orcamento.query.order_by(Orcamento.id.desc()).first()
        if ultimo:
            num = int(ultimo.numero.split('-')[1]) + 1
        else:
            num = 1
        ano = datetime.now().year
        return f'{ano}-{num:05d}'


class ItemOrcamento(db.Model):
    __tablename__ = 'itens_orcamento'

    id = db.Column(db.Integer, primary_key=True)
    orcamento_id = db.Column(db.Integer, db.ForeignKey('orcamentos.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'))
    descricao = db.Column(db.String(200), nullable=False)
    quantidade = db.Column(db.Float, default=1)
    valor_unitario = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<ItemOrcamento {self.descricao}>'

    @property
    def total(self):
        return self.quantidade * self.valor_unitario


# Categorias padrão para movimentações financeiras
CATEGORIAS_ENTRADA = [
    'Vendas',
    'Serviços',
    'Recebimentos',
    'Outros'
]

CATEGORIAS_SAIDA = [
    'Fornecedores',
    'Salários',
    'Aluguel',
    'Água/Luz/Internet',
    'Impostos',
    'Material de escritório',
    'Marketing',
    'Transporte',
    'Manutenção',
    'Outros'
]
