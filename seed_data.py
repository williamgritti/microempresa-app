"""Script para popular o banco com dados de exemplo"""
from datetime import date, timedelta
from app import create_app, db
from app.models import Cliente, Produto, Movimentacao, Orcamento, ItemOrcamento, MovimentacaoEstoque

app = create_app()

with app.app_context():
    # Limpar dados existentes
    ItemOrcamento.query.delete()
    Orcamento.query.delete()
    MovimentacaoEstoque.query.delete()
    Movimentacao.query.delete()
    Produto.query.delete()
    Cliente.query.delete()
    db.session.commit()

    # === CLIENTES ===
    clientes = [
        Cliente(
            nome='Maria Silva',
            documento='12345678901',
            tipo_documento='CPF',
            email='maria@email.com',
            telefone='(11) 99999-1234',
            endereco='Rua das Flores, 123',
            cidade='São Paulo',
            estado='SP',
            cep='01234-567'
        ),
        Cliente(
            nome='João Santos',
            documento='98765432100',
            tipo_documento='CPF',
            email='joao@email.com',
            telefone='(11) 98888-5678',
            endereco='Av. Brasil, 456',
            cidade='São Paulo',
            estado='SP',
            cep='04567-890'
        ),
        Cliente(
            nome='Empresa ABC Ltda',
            documento='12345678000190',
            tipo_documento='CNPJ',
            email='contato@empresaabc.com',
            telefone='(11) 3333-4444',
            endereco='Rua Comercial, 789',
            cidade='São Paulo',
            estado='SP',
            cep='05678-123'
        ),
        Cliente(
            nome='Ana Oliveira',
            documento='11122233344',
            tipo_documento='CPF',
            email='ana@email.com',
            telefone='(21) 97777-8888',
            endereco='Rua do Sol, 100',
            cidade='Rio de Janeiro',
            estado='RJ'
        ),
        Cliente(
            nome='Tech Solutions ME',
            documento='98765432000111',
            tipo_documento='CNPJ',
            email='tech@solutions.com',
            telefone='(11) 2222-3333',
            endereco='Av. Tecnologia, 500',
            cidade='São Paulo',
            estado='SP'
        ),
    ]

    for c in clientes:
        db.session.add(c)
    db.session.commit()
    print(f'✓ {len(clientes)} clientes criados')

    # === PRODUTOS ===
    produtos = [
        Produto(
            codigo='PROD001',
            nome='Notebook Dell Inspiron',
            descricao='Notebook 15.6", Intel i5, 8GB RAM, 256GB SSD',
            categoria='Eletrônicos',
            unidade='UN',
            preco_custo=2500.00,
            preco_venda=3200.00,
            quantidade=5,
            estoque_minimo=2
        ),
        Produto(
            codigo='PROD002',
            nome='Mouse Wireless Logitech',
            descricao='Mouse sem fio, ergonômico',
            categoria='Eletrônicos',
            unidade='UN',
            preco_custo=45.00,
            preco_venda=89.90,
            quantidade=25,
            estoque_minimo=10
        ),
        Produto(
            codigo='PROD003',
            nome='Teclado Mecânico RGB',
            descricao='Teclado mecânico com iluminação RGB',
            categoria='Eletrônicos',
            unidade='UN',
            preco_custo=120.00,
            preco_venda=249.90,
            quantidade=8,
            estoque_minimo=5
        ),
        Produto(
            codigo='PROD004',
            nome='Monitor 24" Full HD',
            descricao='Monitor LED 24 polegadas, 1080p',
            categoria='Eletrônicos',
            unidade='UN',
            preco_custo=650.00,
            preco_venda=899.00,
            quantidade=3,
            estoque_minimo=2
        ),
        Produto(
            codigo='PROD005',
            nome='Cabo HDMI 2m',
            descricao='Cabo HDMI 2.0, 2 metros',
            categoria='Acessórios',
            unidade='UN',
            preco_custo=15.00,
            preco_venda=35.00,
            quantidade=50,
            estoque_minimo=20
        ),
        Produto(
            codigo='PROD006',
            nome='Pen Drive 32GB',
            descricao='Pen drive USB 3.0, 32GB',
            categoria='Acessórios',
            unidade='UN',
            preco_custo=18.00,
            preco_venda=39.90,
            quantidade=30,
            estoque_minimo=15
        ),
        Produto(
            codigo='SERV001',
            nome='Formatação de Computador',
            descricao='Serviço de formatação e instalação de sistema',
            categoria='Serviços',
            unidade='UN',
            preco_custo=0,
            preco_venda=150.00,
            quantidade=999,
            estoque_minimo=0
        ),
        Produto(
            codigo='SERV002',
            nome='Manutenção Preventiva',
            descricao='Limpeza e manutenção preventiva',
            categoria='Serviços',
            unidade='HR',
            preco_custo=0,
            preco_venda=80.00,
            quantidade=999,
            estoque_minimo=0
        ),
    ]

    for p in produtos:
        db.session.add(p)
    db.session.commit()
    print(f'✓ {len(produtos)} produtos criados')

    # === MOVIMENTAÇÕES FINANCEIRAS ===
    hoje = date.today()
    movimentacoes = [
        # Entradas
        Movimentacao(
            tipo='entrada',
            valor=3200.00,
            descricao='Venda Notebook - Maria Silva',
            categoria='Vendas',
            data=hoje - timedelta(days=5),
            pago=True,
            forma_pagamento='PIX',
            cliente_id=1
        ),
        Movimentacao(
            tipo='entrada',
            valor=899.00,
            descricao='Venda Monitor - João Santos',
            categoria='Vendas',
            data=hoje - timedelta(days=3),
            pago=True,
            forma_pagamento='Cartão Crédito',
            cliente_id=2
        ),
        Movimentacao(
            tipo='entrada',
            valor=150.00,
            descricao='Formatação computador',
            categoria='Serviços',
            data=hoje - timedelta(days=2),
            pago=True,
            forma_pagamento='Dinheiro',
            cliente_id=4
        ),
        Movimentacao(
            tipo='entrada',
            valor=1500.00,
            descricao='Contrato manutenção mensal',
            categoria='Serviços',
            data=hoje,
            pago=False,
            data_vencimento=hoje + timedelta(days=15),
            cliente_id=3
        ),
        # Saídas
        Movimentacao(
            tipo='saida',
            valor=2500.00,
            descricao='Compra de notebooks fornecedor',
            categoria='Fornecedores',
            data=hoje - timedelta(days=10),
            pago=True,
            forma_pagamento='Boleto'
        ),
        Movimentacao(
            tipo='saida',
            valor=350.00,
            descricao='Conta de energia',
            categoria='Água/Luz/Internet',
            data=hoje - timedelta(days=8),
            pago=True,
            forma_pagamento='Boleto'
        ),
        Movimentacao(
            tipo='saida',
            valor=1200.00,
            descricao='Aluguel do mês',
            categoria='Aluguel',
            data=hoje - timedelta(days=5),
            pago=True,
            forma_pagamento='Transferência'
        ),
        Movimentacao(
            tipo='saida',
            valor=200.00,
            descricao='Material de escritório',
            categoria='Material de escritório',
            data=hoje - timedelta(days=1),
            pago=True,
            forma_pagamento='Cartão Débito'
        ),
        Movimentacao(
            tipo='saida',
            valor=500.00,
            descricao='Impostos mensais',
            categoria='Impostos',
            data=hoje + timedelta(days=10),
            pago=False,
            data_vencimento=hoje + timedelta(days=10)
        ),
    ]

    for m in movimentacoes:
        db.session.add(m)
    db.session.commit()
    print(f'✓ {len(movimentacoes)} movimentações financeiras criadas')

    # === ORÇAMENTOS ===
    # Orçamento 1 - Pendente
    orc1 = Orcamento(
        numero='2026-00001',
        cliente_id=1,
        data=hoje - timedelta(days=2),
        validade=hoje + timedelta(days=28),
        status='pendente',
        observacoes='Cliente solicitou desconto para pagamento à vista',
        desconto=100.00
    )
    db.session.add(orc1)
    db.session.flush()

    itens_orc1 = [
        ItemOrcamento(orcamento_id=orc1.id, produto_id=1, descricao='Notebook Dell Inspiron', quantidade=1, valor_unitario=3200.00),
        ItemOrcamento(orcamento_id=orc1.id, produto_id=2, descricao='Mouse Wireless Logitech', quantidade=1, valor_unitario=89.90),
        ItemOrcamento(orcamento_id=orc1.id, produto_id=3, descricao='Teclado Mecânico RGB', quantidade=1, valor_unitario=249.90),
    ]
    for item in itens_orc1:
        db.session.add(item)

    # Orçamento 2 - Aprovado
    orc2 = Orcamento(
        numero='2026-00002',
        cliente_id=3,
        data=hoje - timedelta(days=5),
        validade=hoje + timedelta(days=25),
        status='aprovado',
        observacoes='Entrega em 5 dias úteis',
        desconto=0
    )
    db.session.add(orc2)
    db.session.flush()

    itens_orc2 = [
        ItemOrcamento(orcamento_id=orc2.id, produto_id=4, descricao='Monitor 24" Full HD', quantidade=3, valor_unitario=899.00),
        ItemOrcamento(orcamento_id=orc2.id, produto_id=5, descricao='Cabo HDMI 2m', quantidade=3, valor_unitario=35.00),
    ]
    for item in itens_orc2:
        db.session.add(item)

    # Orçamento 3 - Concluído
    orc3 = Orcamento(
        numero='2026-00003',
        cliente_id=5,
        data=hoje - timedelta(days=10),
        validade=hoje + timedelta(days=20),
        status='concluido',
        observacoes='',
        desconto=50.00
    )
    db.session.add(orc3)
    db.session.flush()

    itens_orc3 = [
        ItemOrcamento(orcamento_id=orc3.id, produto_id=7, descricao='Formatação de Computador', quantidade=5, valor_unitario=150.00),
        ItemOrcamento(orcamento_id=orc3.id, produto_id=8, descricao='Manutenção Preventiva', quantidade=10, valor_unitario=80.00),
    ]
    for item in itens_orc3:
        db.session.add(item)

    db.session.commit()
    print('✓ 3 orçamentos criados')

    print('\n✅ Dados de exemplo inseridos com sucesso!')
    print('\nResumo:')
    print(f'   - Clientes: {Cliente.query.count()}')
    print(f'   - Produtos: {Produto.query.count()}')
    print(f'   - Movimentações: {Movimentacao.query.count()}')
    print(f'   - Orçamentos: {Orcamento.query.count()}')
