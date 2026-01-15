from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Cliente

clientes_bp = Blueprint('clientes', __name__)


@clientes_bp.context_processor
def inject_now():
    return {'now': datetime.now}


@clientes_bp.route('/')
def listar():
    busca = request.args.get('busca', '')
    page = request.args.get('page', 1, type=int)

    query = Cliente.query

    if busca:
        query = query.filter(
            (Cliente.nome.ilike(f'%{busca}%')) |
            (Cliente.documento.ilike(f'%{busca}%')) |
            (Cliente.email.ilike(f'%{busca}%'))
        )

    clientes = query.order_by(Cliente.nome).paginate(page=page, per_page=10)

    return render_template('clientes/listar.html', clientes=clientes, busca=busca)


@clientes_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        cliente = Cliente(
            nome=request.form['nome'],
            documento=request.form.get('documento', '').replace('.', '').replace('-', '').replace('/', ''),
            tipo_documento=request.form.get('tipo_documento', 'CPF'),
            email=request.form.get('email'),
            telefone=request.form.get('telefone'),
            endereco=request.form.get('endereco'),
            cidade=request.form.get('cidade'),
            estado=request.form.get('estado'),
            cep=request.form.get('cep'),
            observacoes=request.form.get('observacoes')
        )

        # Verificar documento duplicado
        if cliente.documento:
            existente = Cliente.query.filter_by(documento=cliente.documento).first()
            if existente:
                flash('Já existe um cliente com este documento!', 'error')
                return render_template('clientes/form.html', cliente=cliente)

        try:
            db.session.add(cliente)
            db.session.commit()
            flash('Cliente cadastrado com sucesso!', 'success')
            return redirect(url_for('clientes.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar cliente: {str(e)}', 'error')

    return render_template('clientes/form.html', cliente=None)


@clientes_bp.route('/<int:id>')
def visualizar(id):
    cliente = Cliente.query.get_or_404(id)
    return render_template('clientes/visualizar.html', cliente=cliente)


@clientes_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    cliente = Cliente.query.get_or_404(id)

    if request.method == 'POST':
        cliente.nome = request.form['nome']
        cliente.documento = request.form.get('documento', '').replace('.', '').replace('-', '').replace('/', '')
        cliente.tipo_documento = request.form.get('tipo_documento', 'CPF')
        cliente.email = request.form.get('email')
        cliente.telefone = request.form.get('telefone')
        cliente.endereco = request.form.get('endereco')
        cliente.cidade = request.form.get('cidade')
        cliente.estado = request.form.get('estado')
        cliente.cep = request.form.get('cep')
        cliente.observacoes = request.form.get('observacoes')

        try:
            db.session.commit()
            flash('Cliente atualizado com sucesso!', 'success')
            return redirect(url_for('clientes.visualizar', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar cliente: {str(e)}', 'error')

    return render_template('clientes/form.html', cliente=cliente)


@clientes_bp.route('/<int:id>/excluir', methods=['POST'])
def excluir(id):
    cliente = Cliente.query.get_or_404(id)

    try:
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir cliente: {str(e)}', 'error')

    return redirect(url_for('clientes.listar'))
