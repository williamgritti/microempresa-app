from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, current_app
from app import db
from app.models import Orcamento, ItemOrcamento, Cliente, Produto, Movimentacao
from app.utils.pdf import gerar_pdf_orcamento

orcamentos_bp = Blueprint('orcamentos', __name__)


@orcamentos_bp.context_processor
def inject_now():
    return {'now': datetime.now}


@orcamentos_bp.route('/')
def listar():
    status = request.args.get('status', '')
    busca = request.args.get('busca', '')
    page = request.args.get('page', 1, type=int)

    query = Orcamento.query

    if status:
        query = query.filter(Orcamento.status == status)

    if busca:
        query = query.join(Cliente, isouter=True).filter(
            (Orcamento.numero.ilike(f'%{busca}%')) |
            (Cliente.nome.ilike(f'%{busca}%'))
        )

    orcamentos = query.order_by(Orcamento.created_at.desc()).paginate(page=page, per_page=10)

    return render_template('orcamentos/listar.html', orcamentos=orcamentos, status=status, busca=busca)


@orcamentos_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    clientes = Cliente.query.order_by(Cliente.nome).all()
    produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()

    if request.method == 'POST':
        try:
            data_str = request.form.get('data')
            data = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else date.today()
        except:
            data = date.today()

        validade = None
        if request.form.get('validade'):
            try:
                validade = datetime.strptime(request.form['validade'], '%Y-%m-%d').date()
            except:
                validade = data + timedelta(days=30)
        else:
            validade = data + timedelta(days=30)

        orcamento = Orcamento(
            numero=Orcamento.gerar_numero(),
            cliente_id=request.form.get('cliente_id') or None,
            data=data,
            validade=validade,
            status='pendente',
            observacoes=request.form.get('observacoes'),
            desconto=float(request.form.get('desconto', 0).replace(',', '.') or 0)
        )

        # Processar itens
        descricoes = request.form.getlist('item_descricao[]')
        quantidades = request.form.getlist('item_quantidade[]')
        valores = request.form.getlist('item_valor[]')
        produto_ids = request.form.getlist('item_produto_id[]')

        for i in range(len(descricoes)):
            if descricoes[i].strip():
                item = ItemOrcamento(
                    descricao=descricoes[i],
                    quantidade=float(quantidades[i].replace(',', '.') or 1),
                    valor_unitario=float(valores[i].replace(',', '.').replace('R$', '').strip() or 0),
                    produto_id=produto_ids[i] if produto_ids[i] else None
                )
                orcamento.itens.append(item)

        try:
            db.session.add(orcamento)
            db.session.commit()
            flash('Orçamento criado com sucesso!', 'success')
            return redirect(url_for('orcamentos.visualizar', id=orcamento.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar orçamento: {str(e)}', 'error')

    return render_template('orcamentos/form.html',
                           orcamento=None,
                           clientes=clientes,
                           produtos=produtos)


@orcamentos_bp.route('/<int:id>')
def visualizar(id):
    orcamento = Orcamento.query.get_or_404(id)
    return render_template('orcamentos/visualizar.html', orcamento=orcamento)


@orcamentos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    orcamento = Orcamento.query.get_or_404(id)
    clientes = Cliente.query.order_by(Cliente.nome).all()
    produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()

    if request.method == 'POST':
        try:
            data_str = request.form.get('data')
            orcamento.data = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else orcamento.data
        except:
            pass

        if request.form.get('validade'):
            try:
                orcamento.validade = datetime.strptime(request.form['validade'], '%Y-%m-%d').date()
            except:
                pass

        orcamento.cliente_id = request.form.get('cliente_id') or None
        orcamento.observacoes = request.form.get('observacoes')
        orcamento.desconto = float(request.form.get('desconto', 0).replace(',', '.') or 0)

        # Remover itens antigos
        ItemOrcamento.query.filter_by(orcamento_id=orcamento.id).delete()

        # Adicionar novos itens
        descricoes = request.form.getlist('item_descricao[]')
        quantidades = request.form.getlist('item_quantidade[]')
        valores = request.form.getlist('item_valor[]')
        produto_ids = request.form.getlist('item_produto_id[]')

        for i in range(len(descricoes)):
            if descricoes[i].strip():
                item = ItemOrcamento(
                    orcamento_id=orcamento.id,
                    descricao=descricoes[i],
                    quantidade=float(quantidades[i].replace(',', '.') or 1),
                    valor_unitario=float(valores[i].replace(',', '.').replace('R$', '').strip() or 0),
                    produto_id=produto_ids[i] if produto_ids[i] else None
                )
                db.session.add(item)

        try:
            db.session.commit()
            flash('Orçamento atualizado com sucesso!', 'success')
            return redirect(url_for('orcamentos.visualizar', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar orçamento: {str(e)}', 'error')

    return render_template('orcamentos/form.html',
                           orcamento=orcamento,
                           clientes=clientes,
                           produtos=produtos)


@orcamentos_bp.route('/<int:id>/excluir', methods=['POST'])
def excluir(id):
    orcamento = Orcamento.query.get_or_404(id)

    try:
        db.session.delete(orcamento)
        db.session.commit()
        flash('Orçamento excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir orçamento: {str(e)}', 'error')

    return redirect(url_for('orcamentos.listar'))


@orcamentos_bp.route('/<int:id>/alterar-status', methods=['POST'])
def alterar_status(id):
    orcamento = Orcamento.query.get_or_404(id)
    novo_status = request.form.get('status')

    if novo_status in ['pendente', 'aprovado', 'recusado', 'concluido']:
        orcamento.status = novo_status

        # Se aprovado/concluído, criar movimentação financeira
        if novo_status in ['aprovado', 'concluido']:
            movimentacao_existente = Movimentacao.query.filter_by(orcamento_id=id).first()
            if not movimentacao_existente:
                mov = Movimentacao(
                    tipo='entrada',
                    valor=orcamento.total,
                    descricao=f'Orçamento {orcamento.numero}',
                    categoria='Vendas',
                    data=date.today(),
                    pago=(novo_status == 'concluido'),
                    cliente_id=orcamento.cliente_id,
                    orcamento_id=orcamento.id
                )
                db.session.add(mov)

        try:
            db.session.commit()
            flash(f'Status alterado para {novo_status}!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao alterar status: {str(e)}', 'error')

    return redirect(url_for('orcamentos.visualizar', id=id))


@orcamentos_bp.route('/<int:id>/pdf')
def gerar_pdf(id):
    orcamento = Orcamento.query.get_or_404(id)

    pdf_buffer = gerar_pdf_orcamento(orcamento, current_app.config)

    return Response(
        pdf_buffer.getvalue(),
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'inline; filename=orcamento_{orcamento.numero}.pdf'
        }
    )
