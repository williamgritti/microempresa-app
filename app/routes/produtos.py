from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Produto, MovimentacaoEstoque

produtos_bp = Blueprint('produtos', __name__)


@produtos_bp.context_processor
def inject_now():
    return {'now': datetime.now}


@produtos_bp.route('/')
def listar():
    busca = request.args.get('busca', '')
    filtro = request.args.get('filtro', '')
    page = request.args.get('page', 1, type=int)

    query = Produto.query

    if busca:
        query = query.filter(
            (Produto.nome.ilike(f'%{busca}%')) |
            (Produto.codigo.ilike(f'%{busca}%')) |
            (Produto.categoria.ilike(f'%{busca}%'))
        )

    if filtro == 'estoque_baixo':
        query = query.filter(Produto.quantidade <= Produto.estoque_minimo)
    elif filtro == 'ativos':
        query = query.filter(Produto.ativo == True)
    elif filtro == 'inativos':
        query = query.filter(Produto.ativo == False)

    produtos = query.order_by(Produto.nome).paginate(page=page, per_page=10)

    return render_template('produtos/listar.html', produtos=produtos, busca=busca, filtro=filtro)


@produtos_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        produto = Produto(
            codigo=request.form.get('codigo'),
            nome=request.form['nome'],
            descricao=request.form.get('descricao'),
            categoria=request.form.get('categoria'),
            unidade=request.form.get('unidade', 'UN'),
            preco_custo=float(request.form.get('preco_custo', 0).replace(',', '.') or 0),
            preco_venda=float(request.form.get('preco_venda', 0).replace(',', '.') or 0),
            quantidade=float(request.form.get('quantidade', 0).replace(',', '.') or 0),
            estoque_minimo=float(request.form.get('estoque_minimo', 0).replace(',', '.') or 0),
            ativo=True
        )

        # Verificar código duplicado
        if produto.codigo:
            existente = Produto.query.filter_by(codigo=produto.codigo).first()
            if existente:
                flash('Já existe um produto com este código!', 'error')
                return render_template('produtos/form.html', produto=produto)

        try:
            db.session.add(produto)
            db.session.commit()
            flash('Produto cadastrado com sucesso!', 'success')
            return redirect(url_for('produtos.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar produto: {str(e)}', 'error')

    return render_template('produtos/form.html', produto=None)


@produtos_bp.route('/<int:id>')
def visualizar(id):
    produto = Produto.query.get_or_404(id)
    movimentacoes = MovimentacaoEstoque.query.filter_by(produto_id=id).order_by(
        MovimentacaoEstoque.data.desc()
    ).limit(10).all()
    return render_template('produtos/visualizar.html', produto=produto, movimentacoes=movimentacoes)


@produtos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    produto = Produto.query.get_or_404(id)

    if request.method == 'POST':
        produto.codigo = request.form.get('codigo')
        produto.nome = request.form['nome']
        produto.descricao = request.form.get('descricao')
        produto.categoria = request.form.get('categoria')
        produto.unidade = request.form.get('unidade', 'UN')
        produto.preco_custo = float(request.form.get('preco_custo', 0).replace(',', '.') or 0)
        produto.preco_venda = float(request.form.get('preco_venda', 0).replace(',', '.') or 0)
        produto.estoque_minimo = float(request.form.get('estoque_minimo', 0).replace(',', '.') or 0)
        produto.ativo = 'ativo' in request.form

        try:
            db.session.commit()
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('produtos.visualizar', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar produto: {str(e)}', 'error')

    return render_template('produtos/form.html', produto=produto)


@produtos_bp.route('/<int:id>/excluir', methods=['POST'])
def excluir(id):
    produto = Produto.query.get_or_404(id)

    try:
        db.session.delete(produto)
        db.session.commit()
        flash('Produto excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir produto: {str(e)}', 'error')

    return redirect(url_for('produtos.listar'))


@produtos_bp.route('/<int:id>/movimentar', methods=['GET', 'POST'])
def movimentar(id):
    produto = Produto.query.get_or_404(id)

    if request.method == 'POST':
        tipo = request.form['tipo']
        quantidade = float(request.form['quantidade'].replace(',', '.'))
        motivo = request.form.get('motivo', '')

        if tipo == 'saida' and quantidade > produto.quantidade:
            flash('Quantidade insuficiente em estoque!', 'error')
            return redirect(url_for('produtos.movimentar', id=id))

        movimentacao = MovimentacaoEstoque(
            produto_id=id,
            tipo=tipo,
            quantidade=quantidade,
            motivo=motivo
        )

        if tipo == 'entrada':
            produto.quantidade += quantidade
        else:
            produto.quantidade -= quantidade

        try:
            db.session.add(movimentacao)
            db.session.commit()
            flash(f'Movimentação de estoque registrada!', 'success')
            return redirect(url_for('produtos.visualizar', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar movimentação: {str(e)}', 'error')

    return render_template('produtos/movimentar.html', produto=produto)
