from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle


def create_report_pdf(data, output_path):
    """
    data deve conter as seguintes chaves (todas strings):
      report_code        # ex: "PBO-02-19 B"
      report_date        # ex: "02/19"
      reg_code           # ex: "REG-302"
      pbo_code           # ex: "PBO-02"
      classification     # ex: "CLASSIFICAÇÃO DA MANUTENÇÃO PROGRAMADA"
      info_title         # ex: "INFORMAÇÕES SOBRE CONTINUIDADE"
      inspector          # ex: "RODRIGO"
      delta_t            # ex: "32,8"
      temp_ambient       # ex: "30"
      temp_object        # ex: "62,8"
      agency_region      # ex: "AGÊNCIA REGIONAL DE ITAJAÍ"
      feeder             # ex: ""  (em branco no exemplo)
      equipment          # ex: ""  (em branco no exemplo)
      form_number        # ex: "NOTA Nº 810000068071"
      department_info    # ex: "DIRETORIA DE DISTRIBUIÇÃO DEPARTAMENTO DE MANUTENÇÃO DO SISTEMA ELÉTRICO DIVISÃO DE MANUTENÇÃO DA DISTRIBUIÇÃO"
      dec_atual          # ex: "5.311"
      contrib_dec        # ex: "66.164"
      uc_conjunto        # ex: "9,00"
      uc_possiveis       # ex: "0,73"
      dec_date           # ex: "28/01/19"
      contrib_global     # ex: "0,007"
      situacao_dec       # ex: "BOM"
      location           # ex: "ITAPEMA, MORRETES, BR 101"
      data_value         # ex: "0,290"
      description_long   # texto longo da descrição de componentes
      visual_image_path  # caminho para o arquivo de imagem visual
      thermal_image_path # caminho para o arquivo de imagem térmica
    """
    #Paragraph(str(), blue_style)

    # configura documento
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm
    )
    styles = getSampleStyleSheet()
    story = []
    robot_gettable = ParagraphStyle(name='BlueText', parent=styles['Normal'], textColor=colors.blue)

    # Header with Logo and Codes (Fixed Layout)
    logo = Image(data['logo_path'])
    logo.drawHeight = 25 * mm
    logo.drawWidth = 25 * mm * (648 / 354)  # ≈ 45.75 mm

    # Right column: report metadata
    header_info = [
        [Paragraph(f"<b>Código do Relatório:</b> {data['report_code']}", styles['Normal'])],
        [Paragraph(f"<b>Data:</b> {data['report_date']}", styles['Normal'])],
        [Paragraph(f"<b>Código REG:</b> {data['reg_code']}", styles['Normal'])],
        [Paragraph(f"<b>Código PBO:</b> {data['pbo_code']}", styles['Normal'])],
    ]
    right_col = Table(header_info, colWidths=[100*mm])
    right_col.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))

    # Main table: logo and metadata
    header = Table([[logo, right_col]], colWidths=[50*mm, 130*mm])  # Adjust to match scaled logo
    header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))

    story.extend([header, Spacer(1, 12)])


    # seção de informações
    story.extend([
        Paragraph(data['info_title'], styles['Heading3']),
        Spacer(1,6)
    ])
    info_tbl = Table([
        ['Inspetor:',                   data['inspector']],
        ['ΔT (°C):',                    data['delta_t']],
        ['Temperatura Ambiente (°C):',  data['temp_ambient']],
        ['Temperatura do Objeto (°C):', data['temp_object']],
        ['Operação Recomendada:',       data['operation']],
    ], colWidths=[60*mm, 80*mm])
    info_tbl.setStyle(TableStyle([
        ('FONTNAME',    (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',    (0,0), (-1,-1), 10),
        ('BACKGROUND',  (0,0), (-1,0),   colors.lightgrey),
        ('BOX',         (0,0), (-1,-1), 0.5, colors.black),
        ('INNERGRID',   (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    story.extend([info_tbl, Spacer(1,8)])

    # agência regional e imagem
    story.extend([
    Paragraph(data['agency_region'], styles['Normal']),
    Spacer(1,4),
    Table(
        [[
            Image(data['visual_image_path'], width=80*mm, height=50*mm),
            Image(data['thermal_image_path'], width=80*mm, height=50*mm),
        ]],
        colWidths=[80*mm, 80*mm]
    ),
    Spacer(1,10),
    ])

    # alimentador, equipamento e formulário
    meta_tbl = Table([
        ['Alimentador:', data['feeder']],
        ['Equipamento:', data['equipment']],
        ['Formulário:',  data['form_number']],
        ['Emissividade:', data['emissivity']],
        ['Horario:', data['timestamp'].replace(microsecond=0)]
    ], colWidths=[50*mm, 90*mm])
    meta_tbl.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 10),
        ('INNERGRID',(0,0), (-1,-1), 0.3, colors.grey),
    ]))
    story.extend([meta_tbl, Spacer(1,8)])

    # departamento / diretoria
    story.extend([
        Paragraph(data['department_info'], styles['Normal']),
        Spacer(1,8),
    ])

    # dados de DEC
    dec_tbl = Table([
        ['DEC Atual do Conjunto (hs):',          data['dec_atual']],
        ['Contribuição p/ DEC do Conjunto:',    data['contrib_dec']],
        ['UC do Conjunto:',                     data['uc_conjunto']],
        ['UC Possíveis Afetadas:',              data['uc_possiveis']],
        ['Data:',                               data['dec_date']],
        ['Contribuição Global:',                data['contrib_global']],
        ['Situação do DEC do Conjunto:',        data['situacao_dec']],
    ], colWidths=[70*mm, 70*mm])
    dec_tbl.setStyle(TableStyle([
        ('FONTNAME',    (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',    (0,0), (-1,-1), 10),
        ('BOX',         (0,0), (-1,-1), 0.3, colors.black),
        ('INNERGRID',   (0,0), (-1,-1), 0.3, colors.grey),
    ]))
    story.extend([dec_tbl, Spacer(1,10)])

    # localização, data e descrição longa
    story.extend([
        Paragraph(f"<b>Localização:</b> {data['location']}", styles['Normal']),
        Spacer(1,4),
        Paragraph(f"<b>Data:</b> {data['data_value']}", styles['Normal']),
        Spacer(1,6),
        Paragraph(data['description_long'], styles['Normal']),
        Spacer(1,10),
    ])

    # gera o PDF
    doc.build(story)
