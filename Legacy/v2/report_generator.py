# report_generator.py
import os
import cv2
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm, inch
from reportlab.lib.enums import TA_CENTER
# Import LABEL_TRANSLATION from the other module or define it here if preferred
from v2.image_processing import LABEL_TRANSLATION

class ReportGenerator:
    """Generates a multi-page PDF inspection report from data dictionaries."""

    def __init__(self, report_data, processed_data, temp_dir):
        self.data = report_data
        self.processed_data = processed_data
        self.temp_dir = temp_dir
        self.story = []
        self.styles = getSampleStyleSheet()

    def generate(self, output_path):
        """Builds the full report and saves it to a file."""
        print("Generating PDF report...")
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=15*mm, rightMargin=15*mm,
            topMargin=15*mm, bottomMargin=15*mm
        )

        self._build_summary_page()
        self._build_detailed_component_pages()
        
        doc.build(self.story)
        print(f"PDF report successfully saved to {output_path}")

    def _build_summary_page(self):
        """Builds the first page of the report with summary information."""
        self._create_header()
        self.story.append(Spacer(1, 5 * mm))
        
        # This structure is copied from the original report_Creator.py
        # It creates the summary page based on the data dictionary.
        agency_style = ParagraphStyle(name='AgencyStyle', parent=self.styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=10)
        self.story.append(Paragraph(self.data['agency_region'], agency_style))
        self.story.append(Spacer(1, 5 * mm))

        info_title_style = ParagraphStyle(name='InfoContStyle', parent=self.styles['Normal'], fontName='Helvetica-Bold', fontSize=11, spaceBefore=6, spaceAfter=6)
        self.story.append(Paragraph(self.data['info_title'], info_title_style))
        self._create_dec_table()
        self.story.append(Spacer(1, 5 * mm))

        location_style = ParagraphStyle(name='LocationStyle', parent=self.styles['Normal'], fontSize=9, leading=12)
        self.story.append(Paragraph(f"<b>Localização:</b> {self.data['location']}", location_style))
        self.story.append(Spacer(1, 3 * mm))
        
        self._create_main_images_table()
        self.story.append(Spacer(1, 5 * mm))

        self._create_temperature_table()
        self.story.append(Spacer(1, 5 * mm))

        obs_title_style = ParagraphStyle(name='ObsTitleStyle', parent=self.styles['Normal'], fontName='Helvetica-Bold', fontSize=10)
        self.story.append(Paragraph("<b>OBSERVAÇÕES:</b>", obs_title_style))
        self.story.append(Spacer(1, 2 * mm))
        desc_style = ParagraphStyle(name='DescriptionStyle', parent=self.styles['Normal'], fontSize=9, leading=12)
        self.story.append(Paragraph(self.data['description_long'], desc_style))
        self.story.append(Spacer(1, 8 * mm))

        dept_info_style = ParagraphStyle(name='DeptInfoStyle', parent=self.styles['Normal'], alignment=TA_CENTER, fontSize=8, leading=10)
        self.story.append(Paragraph(self.data['department_info'], dept_info_style))

    def _build_detailed_component_pages(self):
        """Builds pages with details for each detected component."""
        self.story.append(PageBreak())
        
        timestamp_str = self.data['timestamp'].strftime('%d/%m/%Y')
        self.story.append(Paragraph(f"Análise Detalhada dos Componentes - {timestamp_str}", self.styles['Title']))
        self.story.append(Spacer(1, 12))

        self._create_findings_summary_table()
        self.story.append(Spacer(1, 24))

        zoomed_components = self.processed_data['zoomed_components']
        predictions = self.processed_data['predictions']

        if not zoomed_components:
            self.story.append(Paragraph("Nenhum componente foi detectado para análise detalhada.", self.styles['Normal']))
            return

        for i, component in enumerate(zoomed_components):
            self._create_component_detail_section(i, component, predictions[i])
            if i < len(zoomed_components) - 1:
                self.story.append(PageBreak())

    def _create_header(self):
        # Uses self.data dictionary instead of a config object
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
        self.story.append(header_table)

    def _create_dec_table(self):
        # This method and subsequent ones are simplified by directly accessing the `self.data` dict
        data = [
            ['DEC Atual do Conjunto (hs):', self.data['dec_atual']],
            ['Contribuição p/ DEC do Conjunto:', self.data['contrib_dec']],
            ['UC do Conjunto:', self.data['uc_conjunto']],
            ['UC Possíveis Afetadas:', self.data['uc_possiveis']],
            ['Data:', self.data['dec_date']],
            ['Contribuição Global:', self.data['contrib_global']],
            ['Situação do DEC do Conjunto:', self.data['situacao_dec']],
        ]
        tbl = Table(data, colWidths=[70*mm, 90*mm])
        tbl.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOX', (0,0), (-1,-1), 0.5, colors.black), ('INNERGRID', (0,0), (-1,-1), 0.3, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 2*mm)
        ]))
        self.story.append(tbl)
        
    def _create_main_images_table(self):
        visual_path = os.path.join(self.temp_dir, "main_visual.png")
        thermal_path = os.path.join(self.temp_dir, "main_thermal.png")
        cv2.imwrite(visual_path, self.processed_data['annotated_visual'])
        cv2.imwrite(thermal_path, self.processed_data['annotated_thermal'])

        img_width, img_height = 85*mm, (85*mm / 4) * 3
        visual_img = Image(visual_path, width=img_width, height=img_height)
        thermal_img = Image(thermal_path, width=img_width, height=img_height)
        
        tbl = Table([[visual_img, thermal_img]], colWidths=[img_width, img_width], rowHeights=[img_height])
        self.story.append(tbl)
        
    def _create_temperature_table(self):
        data = [
            ['ΔT (°C):', self.data['delta_t']],
            ['Temperatura Ambiente (°C):', self.data['temp_ambient']],
            ['Maior temperatura (°C):', self.data['temp_object']],
            ['Equipamento de maior temperatura:', self.data['temp_max_equipment_value']],
            ['Emissividade:', self.data['emissivity']],
        ]
        tbl = Table(data, colWidths=[70*mm, 90*mm])
        tbl.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOX', (0,0), (-1,-1), 0.5, colors.black), ('INNERGRID', (0,0), (-1,-1), 0.3, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 2*mm)
        ]))
        self.story.append(tbl)
    
    def _create_findings_summary_table(self):
        gps = self.processed_data['gps']
        data = [
            ["Informações Gerais da Inspeção Detalhada", ""],
            ["Coordenadas GPS", f"{gps.lat}, {gps.lon}"],
            ["Temperatura Ambiente", f"{self.processed_data['env_temp']}°C"],
            ["Umidade Relativa", f"{self.processed_data['humidity']*100:.0f}%"],
            ["Emissividade", f"{self.processed_data['emissivity']}"],
            ["Temperatura Máxima Detectada", f"{self.processed_data['max_detected_temp']}°C"],
        ]
        tbl = Table(data, colWidths=[3*inch, 3.5*inch])
        tbl.setStyle(TableStyle([
            ('SPAN', (0, 0), (1, 0)), ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (1, 0), colors.darkslategray),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        self.story.append(tbl)

    def _create_component_detail_section(self, index, component, prediction):
        label = LABEL_TRANSLATION.get(prediction['label'], prediction['label'])
        
        self.story.append(Paragraph(f"Detalhes do Componente {index+1}: {label}", self.styles['h2']))
        self.story.append(Spacer(1, 12))

        # Save and add component images
        visual_path = os.path.join(self.temp_dir, f"comp_{index+1}_visual.png")
        thermal_path = os.path.join(self.temp_dir, f"comp_{index+1}_thermal.png")
        cv2.imwrite(visual_path, component["visual"])
        cv2.imwrite(thermal_path, component["thermal"])
        
        img_visual = Image(visual_path, width=3*inch, height=3*inch, kind='proportional')
        img_thermal = Image(thermal_path, width=3*inch, height=3*inch, kind='proportional')
        
        img_table = Table([[img_visual, img_thermal]], colWidths=[3.2*inch, 3.2*inch])
        self.story.append(img_table)
        self.story.append(Spacer(1, 12))

        # Component details table
        temp = prediction['temp']
        diagnosis = "Atenção Requerida" if temp >= 60 else "Normal"
        bg_color = colors.orange if temp >= 60 else colors.lightgreen

        data = [
            ["Análise do Componente", ""],
            ["Componente", label],
            ["Temperatura Registrada", f"{temp}°C"],
            ["Diagnóstico Preliminar", diagnosis],
            ["Observações", ""]
        ]
        tbl = Table(data, colWidths=[2.5*inch, 4*inch])
        tbl.setStyle(TableStyle([
            ('SPAN', (0, 0), (1, 0)), ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (1, 0), colors.darkslategray),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (1, 2), (1, 2), bg_color),
        ]))
        self.story.append(tbl)