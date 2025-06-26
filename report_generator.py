# report_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER

class ReportGenerator:
    """Generates the summary page of the inspection report."""

    def __init__(self, report_data):
        self.data = report_data
        self.styles = getSampleStyleSheet()

    def generate_summary_story(self):
        """Builds the story list containing the summary page elements."""
        story = []
        # Build all elements for the first page
        story.extend(self._create_header())
        story.append(Spacer(1, 2 * mm)) # This spacer is already small, kept as is.

        agency_style = ParagraphStyle(name='AgencyStyle', parent=self.styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=10)
        story.append(Paragraph(self.data['agency_region'], agency_style))
        story.append(Spacer(1, 3 * mm)) # REDUCED from 5*mm

        info_title_style = ParagraphStyle(name='InfoContStyle', parent=self.styles['Normal'], fontName='Helvetica-Bold', fontSize=11, spaceBefore=6, spaceAfter=6)
        story.append(Paragraph(self.data['info_title'], info_title_style))
        story.append(self._create_dec_table())
        story.append(Spacer(1, 3 * mm)) # REDUCED from 5*mm

        location_style = ParagraphStyle(name='LocationStyle', parent=self.styles['Normal'], fontSize=9, leading=12)
        story.append(Paragraph(f"<b>Localização:</b> {self.data['location']}", location_style))
        story.append(Spacer(1, 3 * mm)) # Kept as is.

        story.append(self._create_main_images_table())
        story.append(Spacer(1, 3 * mm)) # REDUCED from 5*mm

        story.append(self._create_temperature_table())
        story.append(Spacer(1, 3 * mm)) # REDUCED from 5*mm

        obs_title_style = ParagraphStyle(name='ObsTitleStyle', parent=self.styles['Normal'], fontName='Helvetica-Bold', fontSize=10)
        story.append(Paragraph("<b>OBSERVAÇÕES:</b>", obs_title_style))
        story.append(Spacer(1, 2 * mm)) # Kept as is.
        desc_style = ParagraphStyle(name='DescriptionStyle', parent=self.styles['Normal'], fontSize=9, leading=12)
        story.append(Paragraph(self.data['description_long'], desc_style))
        story.append(Spacer(1, 4 * mm)) # SIGNIFICANTLY REDUCED from 8*mm

        dept_info_style = ParagraphStyle(name='DeptInfoStyle', parent=self.styles['Normal'], alignment=TA_CENTER, fontSize=8, leading=10)
        story.append(Paragraph(self.data['department_info'], dept_info_style))
        
        return story

    def _create_header(self):
        logo = Image(self.data['logo_path'], width=45*mm, height=25*mm)
        p_style = ParagraphStyle(name='Header', fontSize=8, leading=10)
        header_table_data = [[
            logo,
            Paragraph(f"<b>Código:</b> {self.data['report_code']}<br/>"
                      f"<b>Horário:</b> {self.data['timestamp'].strftime('%H:%M:%S')}<br/>"
                      f"<b>Inspetor:</b> {self.data['inspector']}", p_style),
            Paragraph(f"<b>Alimentador:</b> {self.data['feeder']}<br/>"
                      f"<b>Equipamento:</b> {self.data['equipment']}<br/>"
                      f"<b>Formulário:</b> {self.data['form_number']}", p_style)
        ]]
        header_table = Table(header_table_data, colWidths=[45*mm, 65*mm, 65*mm])
        header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        return [header_table]

    def _create_dec_table(self):
        data = [['DEC Atual do Conjunto (hs):', self.data['dec_atual']], ['Contribuição p/ DEC do Conjunto:', self.data['contrib_dec']], ['UC do Conjunto:', self.data['uc_conjunto']], ['UC Possíveis Afetadas:', self.data['uc_possiveis']], ['Data:', self.data['dec_date']], ['Contribuição Global:', self.data['contrib_global']], ['Situação do DEC do Conjunto:', self.data['situacao_dec']]]
        tbl = Table(data, colWidths=[70*mm, 90*mm], style=[('FONTNAME', (0,0), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,0), (-1,-1), 9), ('BOX', (0,0), (-1,-1), 0.5, colors.black), ('INNERGRID', (0,0), (-1,-1), 0.3, colors.grey), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 2*mm)])
        return tbl
        
    def _create_main_images_table(self):
        # Uses original, un-annotated images
        img_width, img_height = 85*mm, (85*mm / 4) * 3
        visual_img = Image(self.data['visual_image_path'], width=img_width, height=img_height)
        thermal_img = Image(self.data['thermal_image_path'], width=img_width, height=img_height)
        tbl = Table([[visual_img, thermal_img]], colWidths=[img_width, img_width], rowHeights=[img_height])
        return tbl
        
    def _create_temperature_table(self):
        data = [['ΔT (°C):', self.data['delta_t']], ['Temperatura Ambiente (°C):', self.data['temp_ambient']], ['Maior temperatura (°C):', self.data['temp_object']], ['Equipamento de maior temperatura:', self.data['temp_max_equipment_value']], ['Emissividade:', self.data['emissivity_val']]]
        tbl = Table(data, colWidths=[70*mm, 90*mm], style=[('FONTNAME', (0,0), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,0), (-1,-1), 9), ('BOX', (0,0), (-1,-1), 0.5, colors.black), ('INNERGRID', (0,0), (-1,-1), 0.3, colors.grey), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 2*mm)])
        return tbl