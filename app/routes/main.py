from datetime import datetime, timedelta
from flask import Blueprint, render_template
from sqlalchemy import func
from app import db
from app.models import Cliente, Produto, Movimentacao, Orcamento

main_bp = Blueprint('main', __name__)


@main_bp.context_processor
def inject_now():
    return {'now': datetime.now}


@main_bp.route('/')
@main_bp.route('/dashboard')
def dashboard():
    # Estatísticas gerais
    total_clientes = Cliente.query.count()
    total_produtos = Produto.query.count()

    # Produtos com estoque baixo
    produtos_estoque_baixo = Produto.query.filter(
        Produto.quantidade <= Produto.estoque_minimo,
        Produto.ativo == True
    ).count()

    # Orçamentos pendentes
    orcamentos_pendentes = Orcamento.query.filter_by(status='pendente').count()

    # Movimentações do mês atual
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    entradas_mes = db.session.query(func.sum(Movimentacao.valor)).filter(
        Movimentacao.tipo == 'entrada',
        Movimentacao.data >= inicio_mes.date(),
        Movimentacao.data <= fim_mes.date(),
        Movimentacao.pago == True
    ).scalar() or 0

    saidas_mes = db.session.query(func.sum(Movimentacao.valor)).filter(
        Movimentacao.tipo == 'saida',
        Movimentacao.data >= inicio_mes.date(),
        Movimentacao.data <= fim_mes.date(),
        Movimentacao.pago == True
    ).scalar() or 0

    saldo_mes = entradas_mes - saidas_mes

    # Contas a receber (entradas não pagas)
    contas_receber = db.session.query(func.sum(Movimentacao.valor)).filter(
        Movimentacao.tipo == 'entrada',
        Movimentacao.pago == False
    ).scalar() or 0

    # Contas a pagar (saídas não pagas)
    contas_pagar = db.session.query(func.sum(Movimentacao.valor)).filter(
        Movimentacao.tipo == 'saida',
        Movimentacao.pago == False
    ).scalar() or 0

    # Últimas movimentações
    ultimas_movimentacoes = Movimentacao.query.order_by(
        Movimentacao.created_at.desc()
    ).limit(5).all()

    # Últimos orçamentos
    ultimos_orcamentos = Orcamento.query.order_by(
        Orcamento.created_at.desc()
    ).limit(5).all()

    # Produtos com estoque baixo (lista)
    lista_estoque_baixo = Produto.query.filter(
        Produto.quantidade <= Produto.estoque_minimo,
        Produto.ativo == True
    ).limit(5).all()

    return render_template('dashboard.html',
                           total_clientes=total_clientes,
                           total_produtos=total_produtos,
                           produtos_estoque_baixo=produtos_estoque_baixo,
                           orcamentos_pendentes=orcamentos_pendentes,
                           entradas_mes=entradas_mes,
                           saidas_mes=saidas_mes,
                           saldo_mes=saldo_mes,
                           contas_receber=contas_receber,
                           contas_pagar=contas_pagar,
                           ultimas_movimentacoes=ultimas_movimentacoes,
                           ultimos_orcamentos=ultimos_orcamentos,
                           lista_estoque_baixo=lista_estoque_baixo)
