from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def create_report_pdf_sugestao(data, output_path):
    """
    Generates a PDF report based on the layout of 'sugestao.png'.

    data should contain keys like:
        logo_path, report_code, horario_str, reg_code, pbo_code,
        alimentador, equipamento, form_number, inspector, agency_region,
        info_title, dec_atual, contrib_dec, uc_conjunto, uc_possiveis,
        dec_date, contrib_global, situacao_dec, location,
        visual_image_path, thermal_image_path, delta_t, temp_ambient,
        temp_object_label, temp_object_value, equipment_max_temp_label,
        equipment_max_temp_value, emissivity_label, emissivity_value,
        observations_title, description_long, department_info
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm
    )
    styles = getSampleStyleSheet()
    story = []

    # Custom paragraph styles
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER, parent=styles['Normal'], fontSize=10, leading=12))
    styles.add(ParagraphStyle(name='BoldNormal', parent=styles['Normal'], fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='NormalLeft', alignment=TA_LEFT, parent=styles['Normal'], fontSize=10, spaceBefore=2, spaceAfter=2))
    styles.add(ParagraphStyle(name='HeaderRightColText', parent=styles['NormalLeft'], fontSize=9))


    # --- Header Section ---
    logo = Image(data['logo_path'])
    logo.drawHeight = 20 * mm # Adjusted height
    logo.drawWidth = 20 * mm * (logo.imageWidth / logo.imageHeight) # Maintain aspect ratio

    header_col1_data = [
        [Paragraph(f"<b>Código do Relatório:</b> {data['report_code']}", styles['HeaderRightColText'])],
        [Paragraph(f"<b>Horário:</b> {data['horario_str']}", styles['HeaderRightColText'])],
        [Paragraph(f"<b>Código REG:</b> {data['reg_code']}", styles['HeaderRightColText'])],
        [Paragraph(f"<b>Código PBO:</b> {data['pbo_code']}", styles['HeaderRightColText'])],
    ]
    header_col1_table = Table(header_col1_data, colWidths=[65*mm])
    header_col1_table.setStyle(TableStyle([
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 1),
    ]))

    header_col2_data = [
        [Paragraph(f"<b>Alimentador:</b> {data['alimentador']}", styles['HeaderRightColText'])],
        [Paragraph(f"<b>Equipamento:</b> {data['equipamento']}", styles['HeaderRightColText'])],
        [Paragraph(f"<b>Formulário:</b> {data['form_number']}", styles['HeaderRightColText'])],
        [Paragraph(f"<b>Inspetor:</b> {data['inspector']}", styles['HeaderRightColText'])],
    ]
    header_col2_table = Table(header_col2_data, colWidths=[60*mm])
    header_col2_table.setStyle(TableStyle([
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 1),
    ]))

    header_table_structure = [[logo, header_col1_table, header_col2_table]]
    main_header_table = Table(header_table_structure, colWidths=[logo.drawWidth + 5*mm, 70*mm, 65*mm])
    main_header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (0,0), 0), # Logo padding
    ]))
    story.extend([main_header_table, Spacer(1, 8*mm)])


    # --- Agency Region ---
    story.extend([
        Paragraph(data['agency_region'], styles['Center']),
        Spacer(1, 6*mm)
    ])

    # --- "INFORMAÇÕES SOBRE CONTINUIDADE" Section ---
    story.extend([
        Paragraph(data['info_title'], styles['Heading3']), # Or a custom style if more specific needed
        Spacer(1, 2*mm)
    ])

    dec_data_table_content = [
        [Paragraph('DEC Atual do Conjunto (hs):', styles['NormalLeft']), Paragraph(data['dec_atual'], styles['NormalLeft'])],
        [Paragraph('Contribuição p/ DEC do Conjunto:', styles['NormalLeft']), Paragraph(data['contrib_dec'], styles['NormalLeft'])],
        [Paragraph('UC do Conjunto:', styles['NormalLeft']), Paragraph(data['uc_conjunto'], styles['NormalLeft'])],
        [Paragraph('UC Possíveis Afetadas:', styles['NormalLeft']), Paragraph(data['uc_possiveis'], styles['NormalLeft'])],
        [Paragraph('Data:', styles['NormalLeft']), Paragraph(data['dec_date'], styles['NormalLeft'])],
        [Paragraph('Contribuição Global:', styles['NormalLeft']), Paragraph(data['contrib_global'], styles['NormalLeft'])],
        [Paragraph('Situação do DEC do Conjunto:', styles['NormalLeft']), Paragraph(data['situacao_dec'], styles['NormalLeft'])],
    ]
    dec_table = Table(dec_data_table_content, colWidths=[70*mm, 90*mm])
    dec_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 1),
    ]))
    story.extend([dec_table, Spacer(1, 2*mm)])

    # --- Location ---
    story.extend([
        Paragraph(f"<b>Localização:</b> {data['location']}", styles['NormalLeft']),
        Spacer(1, 6*mm)
    ])

    # --- Images Section ---
    img_visual = Image(data['visual_image_path'], width=88*mm, height=60*mm) # Adjusted size
    img_thermal = Image(data['thermal_image_path'], width=88*mm, height=60*mm) # Adjusted size
    images_table = Table([[img_visual, img_thermal]], colWidths=[90*mm, 90*mm])
    images_table.setStyle(TableStyle([
        ('LEFTPADDING', (0,0), (-1,-1), 1),
        ('RIGHTPADDING', (0,0), (-1,-1), 1),
    ]))
    story.extend([images_table, Spacer(1, 6*mm)])

    # --- Temperature Data Table ---
    temp_data_content = [
        [Paragraph('ΔT (°C):', styles['NormalLeft']), Paragraph(data['delta_t'], styles['NormalLeft'])],
        [Paragraph('Temperatura Ambiente (°C):', styles['NormalLeft']), Paragraph(data['temp_ambient'], styles['NormalLeft'])],
        [Paragraph(data['temp_object_label'], styles['NormalLeft']), Paragraph(data['temp_object_value'], styles['NormalLeft'])],
        [Paragraph(data['equipment_max_temp_label'], styles['NormalLeft']), Paragraph(data['equipment_max_temp_value'], styles['NormalLeft'])],
        [Paragraph(data['emissivity_label'], styles['NormalLeft']), Paragraph(data['emissivity_value'], styles['NormalLeft'])],
    ]
    temp_table = Table(temp_data_content, colWidths=[70*mm, 90*mm])
    temp_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 1),
    ]))
    story.extend([temp_table, Spacer(1, 6*mm)])

    # --- "OBSERVAÇÕES" Section ---
    story.extend([
        Paragraph(f"<b>{data['observations_title']}</b>", styles['NormalLeft']),
        Spacer(1, 1*mm),
        Paragraph(data['description_long'], styles['NormalLeft']),
        Spacer(1, 8*mm)
    ])

    # --- Department Info (Footer Text) ---
    department_style = ParagraphStyle(name='FooterText', parent=styles['Normal'], fontSize=9, alignment=TA_LEFT)
    story.extend([
        Paragraph(data['department_info'], department_style),
    ])

    doc.build(story)

if __name__ == '__main__':
    # Example usage:
    # Create dummy image files for testing if you don't have them
    # (You should replace these with actual paths to your images)
    dummy_logo_path = "dummy_logo.png"
    dummy_visual_path = "dummy_visual.png"
    dummy_thermal_path = "dummy_thermal.png"

    try:
        from PIL import Image as PILImage
        # Create tiny placeholder PNGs if they don't exist
        if not Path(dummy_logo_path).exists():
            PILImage.new('RGB', (100, 100), color = 'blue').save(dummy_logo_path)
        if not Path(dummy_visual_path).exists():
            PILImage.new('RGB', (400, 300), color = 'green').save(dummy_visual_path)
        if not Path(dummy_thermal_path).exists():
            PILImage.new('RGB', (400, 300), color = 'red').save(dummy_thermal_path)
    except ImportError:
        print("PIL (Pillow) is not installed. Cannot create dummy images. Please create them manually or install Pillow.")
        # As a fallback, create empty files so Image() doesn't fail on path not found
        open(dummy_logo_path, 'a').close()
        open(dummy_visual_path, 'a').close()
        open(dummy_thermal_path, 'a').close()
    except Exception as e:
        print(f"Error creating dummy images: {e}")

    from pathlib import Path
    example_data_sugestao = {
        'logo_path': dummy_logo_path,
        'report_code': "PBO-02-19 B",
        'horario_str': "2025-05-20 13:38:45",
        'reg_code': "REG-302",
        'pbo_code': "PBO-02",
        'alimentador': "ALIMENTADOR",
        'equipamento': "EQUIPAMENTO",
        'form_number': "NOTA Nº 81000",
        'inspector': "RODRIGO",

        'agency_region': "AGÊNCIA REGIONAL DE ITAJAÍ",

        'info_title': "INFORMAÇÕES SOBRE CONTINUIDADE",
        'dec_atual': "5.311",
        'contrib_dec': "66.164",
        'uc_conjunto': "9,00",
        'uc_possiveis': "0,73",
        'dec_date': "28/01/19",
        'contrib_global': "0,007",
        'situacao_dec': "BOM",
        'location': "ITAPEMA, MORRETES, BR 101",

        'visual_image_path': dummy_visual_path,
        'thermal_image_path': dummy_thermal_path,

        'delta_t': "32,8",
        'temp_ambient': "30",
        'temp_object_label': "Maior temperatura (°C):",
        'temp_object_value': "62,8",
        'equipment_max_temp_label': "Equipamento de maior temperatura:",
        'equipment_max_temp_value': "Isolador",
        'emissivity_label': "Emissividade:",
        'emissivity_value': "Emissividade",

        'observations_title': "OBSERVAÇÕES:",
        'description_long': "TERMINAL SUPERIOR DA BY PASS LADO FONTE DA FASE DE DENTRO, TERMINAL INFERIOR DA BY PASS LADO FONTE DA FASE DE FORA, CONTATO SUPERIOR DA BY PASS LADO CARGA DA FASE DE FORA, TERMINAL E CONTATO SUPERIOR DA BY PASS LADO FONTE DA FASE DO MEIO",

        'department_info': "DIRETORIA DE DISTRIBUIÇÃO DEPARTAMENTO DE MANUTENÇÃO DO SISTEMA ELÉTRICO DIVISÃO DE MANUTENÇÃO DA DISTRIBUIÇÃO (RODAPÉ)"
    }

    output_pdf_path_sugestao = "relatorio_sugestao_output.pdf"
    create_report_pdf_sugestao(example_data_sugestao, output_pdf_path_sugestao)
    print(f"Generated PDF: {output_pdf_path_sugestao}")