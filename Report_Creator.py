from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.utils import ImageReader

def create_report_pdf(data, output_path):
    """
    data deve conter as seguintes chaves (strings, unless specified otherwise):
      logo_path, report_code, timestamp (datetime object), reg_code, pbo_code,
      feeder, equipment, form_number, inspector, agency_region, info_title,
      dec_atual, contrib_dec, uc_conjunto, uc_possiveis, dec_date,
      contrib_global, situacao_dec, location, visual_image_path,
      thermal_image_path, delta_t, temp_ambient, temp_object, emissivity,
      temp_max_equipment_value, description_long, department_info,
      masked_image_path
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm
    )
    styles = getSampleStyleSheet()
    story = []

    # --- Header Section ---
    # (Your existing code for header section...)
    max_logo_width = 45 * mm
    max_logo_height = 25 * mm
    logo = Image(data['logo_path'], width=max_logo_width, height=max_logo_height)
    header_details_style = ParagraphStyle(name='HeaderDetail', parent=styles['Normal'], fontSize=8, leading=10)
    header_info_col1 = [
        [Paragraph(f"<b>Código do Relatório:</b> {data['report_code']}", header_details_style)],
        [Paragraph(f"<b>Horário:</b> {data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}", header_details_style)],
        [Paragraph(f"<b>Código REG:</b> {data['reg_code']}", header_details_style)],
        [Paragraph(f"<b>Código PBO:</b> {data['pbo_code']}", header_details_style)],
    ]
    header_info_col2 = [
        [Paragraph(f"<b>Alimentador:</b> {data['feeder']}", header_details_style)],
        [Paragraph(f"<b>Equipamento:</b> {data['equipment']}", header_details_style)],
        [Paragraph(f"<b>Formulário:</b> {data['form_number']}", header_details_style)],
        [Paragraph(f"<b>Inspetor:</b> {data['inspector']}", header_details_style)],
    ]
    table_info_col1 = Table(header_info_col1, colWidths=[60*mm])
    table_info_col1.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
    table_info_col2 = Table(header_info_col2, colWidths=[65*mm])
    table_info_col2.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
    header_right_data_table = Table([[table_info_col1, table_info_col2]], colWidths=[60*mm, 65*mm])
    header_right_data_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    header_table = Table([[logo, header_right_data_table]], colWidths=[logo.drawWidth + 5*mm, 125*mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (1,0), (1,0), 3*mm),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 5*mm))

    # --- Agency Region ---
    agency_style = ParagraphStyle(name='AgencyStyle', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=10)
    story.append(Paragraph(data['agency_region'], agency_style))
    story.append(Spacer(1, 5*mm))

    # --- "INFORMAÇÕES SOBRE CONTINUIDADE" Section Title ---
    info_continuidade_style = ParagraphStyle(name='InfoContStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, spaceBefore=6, spaceAfter=6)
    story.append(Paragraph(data['info_title'], info_continuidade_style))

    # --- DEC Table ---
    # (Your existing code for DEC table...)
    dec_tbl_data = [
        [Paragraph('DEC Atual do Conjunto (hs):', styles['Normal']), Paragraph(data['dec_atual'], styles['Normal'])],
        [Paragraph('Contribuição p/ DEC do Conjunto:', styles['Normal']), Paragraph(data['contrib_dec'], styles['Normal'])],
        [Paragraph('UC do Conjunto:', styles['Normal']), Paragraph(data['uc_conjunto'], styles['Normal'])],
        [Paragraph('UC Possíveis Afetadas:', styles['Normal']), Paragraph(data['uc_possiveis'], styles['Normal'])],
        [Paragraph('Data:', styles['Normal']), Paragraph(data['dec_date'], styles['Normal'])],
        [Paragraph('Contribuição Global:', styles['Normal']), Paragraph(data['contrib_global'], styles['Normal'])],
        [Paragraph('Situação do DEC do Conjunto:', styles['Normal']), Paragraph(data['situacao_dec'], styles['Normal'])],
    ]
    dec_tbl = Table(dec_tbl_data, colWidths=[70*mm, 90*mm])
    dec_tbl.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black), ('INNERGRID', (0,0), (-1,-1), 0.3, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 2*mm),
        ('RIGHTPADDING', (0,0), (-1,-1), 2*mm), ('TOPPADDING', (0,0), (-1,-1), 1.5*mm),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5*mm),
    ]))
    story.append(dec_tbl)
    story.append(Spacer(1, 5*mm))

    # --- Localização ---
    location_style = ParagraphStyle(name='LocationStyle', parent=styles['Normal'], fontSize=9, leading=12)
    story.append(Paragraph(f"<b>Localização:</b> {data['location']}", location_style))
    story.append(Spacer(1, 3*mm))

    # --- Images ---
    # (Your existing code for visual and thermal images...)
    img_width_val = 85*mm # Renamed from img_width to avoid conflict if this script is merged differently
    img_height_val = (img_width_val / 4) * 3
    try:
        visual_img = Image(data['visual_image_path'], width=img_width_val, height=img_height_val)
    except Exception as e:
        visual_img = Paragraph(f"Error loading visual image: {e}", styles['Normal'])
        print(f"Error loading visual image: {data['visual_image_path']} - {e}")
    try:
        thermal_img = Image(data['thermal_image_path'], width=img_width_val, height=img_height_val)
    except Exception as e:
        thermal_img = Paragraph(f"Error loading thermal image: {e}", styles['Normal'])
        print(f"Error loading thermal image: {data['thermal_image_path']} - {e}")
    images_table = Table([[visual_img, thermal_img]], colWidths=[img_width_val, img_width_val], rowHeights=[img_height_val])
    images_table.setStyle(TableStyle([
        ('LEFTPADDING', (0,0), (-1,-1), 1*mm), ('RIGHTPADDING', (0,0), (-1,-1), 1*mm),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(images_table)
    story.append(Spacer(1, 5*mm))

    # --- Temperature Table ---
    temp_data_table_style = TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black), ('INNERGRID', (0,0), (-1,-1), 0.3, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 2*mm),
        ('RIGHTPADDING', (0,0), (-1,-1), 2*mm), ('TOPPADDING', (0,0), (-1,-1), 1.5*mm),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5*mm),
    ])
    temp_data = [
        [Paragraph('ΔT (°C):', styles['Normal']), Paragraph(data['delta_t'], styles['Normal'])],
        [Paragraph('Temperatura Ambiente (°C):', styles['Normal']), Paragraph(data['temp_ambient'], styles['Normal'])],
        [Paragraph('Maior temperatura (°C):', styles['Normal']), Paragraph(data['temp_object'], styles['Normal'])],
        [Paragraph('Equipamento de maior temperatura:', styles['Normal']), Paragraph(data['temp_max_equipment_value'], styles['Normal'])],
        [Paragraph('Emissividade:', styles['Normal']), Paragraph(data['emissivity'], styles['Normal'])],
    ]
    temp_table = Table(temp_data, colWidths=[70*mm, 90*mm])
    temp_table.setStyle(temp_data_table_style)
    story.append(temp_table)
    story.append(Spacer(1, 5*mm))

    # --- Observações Section ---
    obs_title_style = ParagraphStyle(name='ObsTitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10)
    story.append(Paragraph("<b>OBSERVAÇÕES:</b>", obs_title_style))
    story.append(Spacer(1, 2*mm))
    desc_style = ParagraphStyle(name='DescriptionStyle', parent=styles['Normal'], fontSize=9, leading=12)
    story.append(Paragraph(data['description_long'], desc_style))
    story.append(Spacer(1, 8*mm)) # More space before footer

    # --- Department Info (Footer-like) ---
    dept_info_style = ParagraphStyle(name='DeptInfoStyle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, leading=10)
    story.append(Paragraph(data['department_info'], dept_info_style))


    # --- Masked Image on a New Page ---
    if 'masked_image_path' in data and data['masked_image_path']:
        story.append(PageBreak())

        # doc.width and doc.height are page_size - margins
        # These seem to be slightly larger than the actual frame for 'Later' pages.
        doc_calc_width = doc.width
        doc_calc_height = doc.height

        # Define the dimensions for the centering Table.
        # This table must fit into the actual page frame.
        # Let's make it 95% of the initially calculated doc_calc_width/height
        # to ensure it's smaller than the problematic frame dimensions from the error.
        table_total_width = doc_calc_width * 0.95
        table_total_height = doc_calc_height * 0.95
        # These dimensions (approx 484.7pt x 719.0pt) should be smaller than
        # the frame reported in error (498.2pt x 744.8pt).

        try:
            img_path = data['masked_image_path']
            reader = ImageReader(img_path)
            orig_w, orig_h = reader.getSize()

            if orig_w == 0 or orig_h == 0:
                raise ValueError("Masked image original width or height is zero.")

            # The image needs to be scaled to fit within the table_total_width/height.
            # So, the bounding box for image scaling is the table's dimensions.
            max_w_for_image = table_total_width
            max_h_for_image = table_total_height

            # Calculate scaling factors
            ratio_w = max_w_for_image / orig_w
            ratio_h = max_h_for_image / orig_h

            if ratio_w < ratio_h:
                # Width is the limiting factor for the image
                final_img_w = max_w_for_image
                final_img_h = orig_h * ratio_w
            else:
                # Height is the limiting factor for the image (or ratios are equal)
                final_img_h = max_h_for_image
                final_img_w = orig_w * ratio_h
            
            masked_image_scaled = Image(
                img_path,
                width=final_img_w,  # Scaled to fit within table_total_width
                height=final_img_h  # Scaled to fit within table_total_height
            )

            # The centering table will now have dimensions table_total_width x table_total_height
            centering_table_data = [[masked_image_scaled]]
            centering_table = Table(
                centering_table_data,
                colWidths=[table_total_width],   # Use the reduced width
                rowHeights=[table_total_height]  # Use the reduced height
            )
            centering_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (0,0), 'CENTER'),      # Center image horizontally in cell
                ('VALIGN', (0,0), (0,0), 'MIDDLE'),     # Center image vertically in cell
            ]))
            story.append(centering_table)

        except Exception as e:
            error_message = f"Error loading, scaling, or adding masked image: {data.get('masked_image_path', 'Path not found')} - {type(e).__name__}: {e}"
            story.append(Paragraph(error_message, styles['Normal']))
            print(error_message)

    # Build the PDF
    doc.build(story)