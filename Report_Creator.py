from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    Image, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import mm

def create_report_pdf(data: dict, output_path: str):
    # Chaves esperadas em `data`:
    # 'report_code', 'report_date', 'reg_code', 'pbo_code',
    # 'classification', 'info_title', 'inspector', 'delta_t',
    # 'temp_ambient', 'temp_object', 'agency_region', 'feeder',
    # 'equipment', 'form_number', 'department_info', 'dec_atual',
    # 'contrib_dec', 'uc_conjunto', 'uc_possiveis', 'dec_date',
    # 'contrib_global', 'situacao_dec', 'location', 'data_value',
    # 'description_long', 'image_path'

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm
    )
    styles = getSampleStyleSheet()
    story = []

    # Cabeçalho com códigos
    header_data = [[
        data['report_code'], data['report_date'],
        data['reg_code'], data['pbo_code']
    ]]
    tbl = Table(header_data, colWidths=[50*mm, 30*mm, 50*mm, 30*mm])
    tbl.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',  (0,0), (-1,-1), 12),
        ('ALIGN',    (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 6))

    # Título da classificação
    story.append(Paragraph(data['classification'], styles['Heading2']))
    story.append(Spacer(1, 4))

    # Seção de informações sobre continuidade
    story.append(Paragraph(data['info_title'], styles['Heading3']))
    story.append(Spacer(1, 6))

    info_data = [
        ['Inspetor:', data['inspector']],
        ['ΔT (°C):', data['delta_t']],
        ['Temperatura Ambiente (°C):', data['temp_ambient']],
        ['Temperatura do Objeto (°C):', data['temp_object']],
    ]
    info_tbl = Table(info_data, colWidths=[60*mm, 80*mm])
    info_tbl.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('BOX',       (0,0), (-1,-1), 0.5, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 8))

    # Agência regional e imagem
    story.append(Paragraph(data['agency_region'], styles['Normal']))
    story.append(Spacer(1, 4))

    img = Image(data['image_path'], width=80*mm, height=50*mm)
    story.append(img)
    story.append(Spacer(1, 10))

    # Alimentador, equipamento e formulário
    meta_data = [
        ['Alimentador:', data['feeder']],
        ['Equipamento:', data['equipment']],
        ['Formulário:', data['form_number']],
    ]
    meta_tbl = Table(meta_data, colWidths=[50*mm, 90*mm])
    meta_tbl.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 10),
        ('INNERGRID', (0,0), (-1,-1), 0.3, colors.grey),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 8))

    # Departamento / informações longas
    story.append(Paragraph(data['department_info'], styles['Normal']))
    story.append(Spacer(1, 8))

    # Dados de DEC
    dec_data = [
        ['DEC Atual do Conjunto (hs):', data['dec_atual']],
        ['Contribuição p/ DEC do Conjunto:', data['contrib_dec']],
        ['UC do Conjunto:', data['uc_conjunto']],
        ['UC Possíveis Afetadas:', data['uc_possiveis']],
        ['Data:', data['dec_date']],
        ['Contribuição Global:', data['contrib_global']],
        ['Situação do DEC do Conjunto:', data['situacao_dec']],
    ]
    dec_tbl = Table(dec_data, colWidths=[70*mm, 70*mm])
    dec_tbl.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 10),
        ('BOX',       (0,0), (-1,-1), 0.3, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.3, colors.grey),
    ]))
    story.append(dec_tbl)
    story.append(Spacer(1, 10))

    # Localização, data e descrição longa
    story.append(Paragraph(f"<b>Localização:</b> {data['location']}", styles['Normal']))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Data:</b> {data['data_value']}", styles['Normal']))
    story.append(Spacer(1, 6))
    story.append(Paragraph(data['description_long'], styles['Normal']))
    story.append(Spacer(1, 10))

    # Gera o PDF
    doc.build(story)