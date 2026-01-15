from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import func
from app import db
from app.models import Movimentacao, Cliente, CATEGORIAS_ENTRADA, CATEGORIAS_SAIDA

financeiro_bp = Blueprint('financeiro', __name__)


@financeiro_bp.context_processor
def inject_now():
    return {'now': datetime.now}


@financeiro_bp.route('/')
def listar():
    tipo = request.args.get('tipo', '')
    status = request.args.get('status', '')
    mes = request.args.get('mes', '')
    page = request.args.get('page', 1, type=int)

    query = Movimentacao.query

    if tipo:
        query = query.filter(Movimentacao.tipo == tipo)

    if status == 'pago':
        query = query.filter(Movimentacao.pago == True)
    elif status == 'pendente':
        query = query.filter(Movimentacao.pago == False)

    if mes:
        try:
            ano, mes_num = mes.split('-')
            data_inicio = date(int(ano), int(mes_num), 1)
            if int(mes_num) == 12:
                data_fim = date(int(ano) + 1, 1, 1) - timedelta(days=1)
            else:
                data_fim = date(int(ano), int(mes_num) + 1, 1) - timedelta(days=1)
            query = query.filter(Movimentacao.data >= data_inicio, Movimentacao.data <= data_fim)
        except:
            pass

    movimentacoes = query.order_by(Movimentacao.data.desc()).paginate(page=page, per_page=15)

    # Totais
    total_entradas = db.session.query(func.sum(Movimentacao.valor)).filter(
        Movimentacao.tipo == 'entrada', Movimentacao.pago == True
    ).scalar() or 0

    total_saidas = db.session.query(func.sum(Movimentacao.valor)).filter(
        Movimentacao.tipo == 'saida', Movimentacao.pago == True
    ).scalar() or 0

    saldo = total_entradas - total_saidas

    return render_template('financeiro/listar.html',
                           movimentacoes=movimentacoes,
                           tipo=tipo,
                           status=status,
                           mes=mes,
                           total_entradas=total_entradas,
                           total_saidas=total_saidas,
                           saldo=saldo)


@financeiro_bp.route('/nova', methods=['GET', 'POST'])
@financeiro_bp.route('/nova/<tipo_mov>', methods=['GET', 'POST'])
def nova(tipo_mov='entrada'):
    clientes = Cliente.query.order_by(Cliente.nome).all()

    if request.method == 'POST':
        try:
            data_str = request.form['data']
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
        except:
            data = date.today()

        data_vencimento = None
        if request.form.get('data_vencimento'):
            try:
                data_vencimento = datetime.strptime(request.form['data_vencimento'], '%Y-%m-%d').date()
            except:
                pass

        movimentacao = Movimentacao(
            tipo=request.form['tipo'],
            valor=float(request.form['valor'].replace(',', '.').replace('R$', '').strip()),
            descricao=request.form['descricao'],
            categoria=request.form.get('categoria'),
            data=data,
            data_vencimento=data_vencimento,
            pago='pago' in request.form,
            forma_pagamento=request.form.get('forma_pagamento'),
            cliente_id=request.form.get('cliente_id') or None
        )

        try:
            db.session.add(movimentacao)
            db.session.commit()
            flash('Movimentação registrada com sucesso!', 'success')
            return redirect(url_for('financeiro.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar movimentação: {str(e)}', 'error')

    return render_template('financeiro/form.html',
                           movimentacao=None,
                           tipo_mov=tipo_mov,
                           clientes=clientes,
                           categorias_entrada=CATEGORIAS_ENTRADA,
                           categorias_saida=CATEGORIAS_SAIDA)


@financeiro_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    movimentacao = Movimentacao.query.get_or_404(id)
    clientes = Cliente.query.order_by(Cliente.nome).all()

    if request.method == 'POST':
        try:
            data_str = request.form['data']
            movimentacao.data = datetime.strptime(data_str, '%Y-%m-%d').date()
        except:
            pass

        if request.form.get('data_vencimento'):
            try:
                movimentacao.data_vencimento = datetime.strptime(request.form['data_vencimento'], '%Y-%m-%d').date()
            except:
                pass
        else:
            movimentacao.data_vencimento = None

        movimentacao.tipo = request.form['tipo']
        movimentacao.valor = float(request.form['valor'].replace(',', '.').replace('R$', '').strip())
        movimentacao.descricao = request.form['descricao']
        movimentacao.categoria = request.form.get('categoria')
        movimentacao.pago = 'pago' in request.form
        movimentacao.forma_pagamento = request.form.get('forma_pagamento')
        movimentacao.cliente_id = request.form.get('cliente_id') or None

        try:
            db.session.commit()
            flash('Movimentação atualizada com sucesso!', 'success')
            return redirect(url_for('financeiro.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar movimentação: {str(e)}', 'error')

    return render_template('financeiro/form.html',
                           movimentacao=movimentacao,
                           tipo_mov=movimentacao.tipo,
                           clientes=clientes,
                           categorias_entrada=CATEGORIAS_ENTRADA,
                           categorias_saida=CATEGORIAS_SAIDA)


@financeiro_bp.route('/<int:id>/excluir', methods=['POST'])
def excluir(id):
    movimentacao = Movimentacao.query.get_or_404(id)

    try:
        db.session.delete(movimentacao)
        db.session.commit()
        flash('Movimentação excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir movimentação: {str(e)}', 'error')

    return redirect(url_for('financeiro.listar'))


@financeiro_bp.route('/<int:id>/marcar-pago', methods=['POST'])
def marcar_pago(id):
    movimentacao = Movimentacao.query.get_or_404(id)
    movimentacao.pago = not movimentacao.pago

    try:
        db.session.commit()
        status = 'pago' if movimentacao.pago else 'pendente'
        flash(f'Movimentação marcada como {status}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar status: {str(e)}', 'error')

    return redirect(url_for('financeiro.listar'))


@financeiro_bp.route('/relatorio')
def relatorio():
    mes = request.args.get('mes', date.today().strftime('%Y-%m'))

    try:
        ano, mes_num = mes.split('-')
        data_inicio = date(int(ano), int(mes_num), 1)
        if int(mes_num) == 12:
            data_fim = date(int(ano) + 1, 1, 1) - timedelta(days=1)
        else:
            data_fim = date(int(ano), int(mes_num) + 1, 1) - timedelta(days=1)
    except:
        data_inicio = date.today().replace(day=1)
        data_fim = (data_inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    # Entradas por categoria
    entradas = db.session.query(
        Movimentacao.categoria,
        func.sum(Movimentacao.valor).label('total')
    ).filter(
        Movimentacao.tipo == 'entrada',
        Movimentacao.data >= data_inicio,
        Movimentacao.data <= data_fim,
        Movimentacao.pago == True
    ).group_by(Movimentacao.categoria).all()

    # Saídas por categoria
    saidas = db.session.query(
        Movimentacao.categoria,
        func.sum(Movimentacao.valor).label('total')
    ).filter(
        Movimentacao.tipo == 'saida',
        Movimentacao.data >= data_inicio,
        Movimentacao.data <= data_fim,
        Movimentacao.pago == True
    ).group_by(Movimentacao.categoria).all()

    total_entradas = sum(e.total or 0 for e in entradas)
    total_saidas = sum(s.total or 0 for s in saidas)
    saldo = total_entradas - total_saidas

    return render_template('financeiro/relatorio.html',
                           mes=mes,
                           data_inicio=data_inicio,
                           data_fim=data_fim,
                           entradas=entradas,
                           saidas=saidas,
                           total_entradas=total_entradas,
                           total_saidas=total_saidas,
                           saldo=saldo)
