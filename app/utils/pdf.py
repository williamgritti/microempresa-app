from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


def gerar_pdf_orcamento(orcamento, config):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm)
    elements = []
    styles = getSampleStyleSheet()

    # Estilos personalizados
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,
        spaceAfter=20
    )

    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=10
    )

    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10
    )

    # Cabeçalho
    empresa_nome = config.get('EMPRESA_NOME', 'Minha Empresa')
    elements.append(Paragraph(empresa_nome, titulo_style))

    if config.get('EMPRESA_CNPJ'):
        elements.append(Paragraph(f"CNPJ: {config['EMPRESA_CNPJ']}", normal_style))
    if config.get('EMPRESA_ENDERECO'):
        elements.append(Paragraph(config['EMPRESA_ENDERECO'], normal_style))
    if config.get('EMPRESA_TELEFONE'):
        elements.append(Paragraph(f"Tel: {config['EMPRESA_TELEFONE']}", normal_style))

    elements.append(Spacer(1, 20))

    # Título do orçamento
    elements.append(Paragraph(f"ORÇAMENTO Nº {orcamento.numero}", subtitulo_style))

    # Informações do orçamento
    info_data = [
        ['Data:', orcamento.data.strftime('%d/%m/%Y'),
         'Validade:', orcamento.validade.strftime('%d/%m/%Y') if orcamento.validade else '-'],
        ['Status:', orcamento.status.capitalize(), '', '']
    ]

    if orcamento.cliente:
        info_data.append(['Cliente:', orcamento.cliente.nome, '', ''])
        if orcamento.cliente.documento:
            info_data.append([f'{orcamento.cliente.tipo_documento}:', orcamento.cliente.documento, '', ''])
        if orcamento.cliente.telefone:
            info_data.append(['Telefone:', orcamento.cliente.telefone, '', ''])

    info_table = Table(info_data, colWidths=[3*cm, 6*cm, 3*cm, 5*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))

    # Itens do orçamento
    elements.append(Paragraph("ITENS", subtitulo_style))

    items_data = [['#', 'Descrição', 'Qtd', 'Valor Unit.', 'Total']]

    for i, item in enumerate(orcamento.itens, 1):
        items_data.append([
            str(i),
            item.descricao[:50],
            f"{item.quantidade:.2f}",
            f"R$ {item.valor_unitario:.2f}",
            f"R$ {item.total:.2f}"
        ])

    items_table = Table(items_data, colWidths=[1*cm, 9*cm, 2*cm, 3*cm, 3*cm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 10))

    # Totais
    totais_data = [
        ['', '', '', 'Subtotal:', f"R$ {orcamento.subtotal:.2f}"],
    ]

    if orcamento.desconto > 0:
        totais_data.append(['', '', '', 'Desconto:', f"R$ {orcamento.desconto:.2f}"])

    totais_data.append(['', '', '', 'TOTAL:', f"R$ {orcamento.total:.2f}"])

    totais_table = Table(totais_data, colWidths=[1*cm, 9*cm, 2*cm, 3*cm, 3*cm])
    totais_table.setStyle(TableStyle([
        ('FONTNAME', (3, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('LINEABOVE', (3, -1), (-1, -1), 1, colors.black),
    ]))
    elements.append(totais_table)

    # Observações
    if orcamento.observacoes:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("OBSERVAÇÕES", subtitulo_style))
        elements.append(Paragraph(orcamento.observacoes, normal_style))

    # Rodapé
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("_" * 50, normal_style))
    elements.append(Paragraph("Assinatura do Cliente", ParagraphStyle('Center', parent=normal_style, alignment=1)))

    doc.build(elements)
    buffer.seek(0)
    return buffer
