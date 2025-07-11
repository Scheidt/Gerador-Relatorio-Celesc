# part_analysis.py
import os
import cv2
import random
import numpy as np
from datetime import datetime
from ultralytics import YOLO
from reportlab.platypus import Paragraph, Table, TableStyle, Image, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

class ComponentAnalyzer:
    """
    Performs detailed component analysis by processing pre-computed model results,
    and adds the results to a report story.
    """
    def __init__(self, report_main_data):
        self.main_data = report_main_data
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='BoldLeft', parent=self.styles['Normal'], fontName='Helvetica-Bold', alignment=TA_LEFT))
        self.styles.add(ParagraphStyle(name='ComponentTitle', parent=self.styles['h2'], alignment=TA_LEFT))
        self.label_translation = report_main_data.get('label_translation', {})
        self.diagnosis_function = report_main_data.get('diagnosis_function')
        
    def _predict_and_process(self, results, visual_img, thermal_img):
        """Processes pre-computed prediction results to generate necessary data."""
        print("Processing pre-computed results to extract components...")
        
        h_visual, w_visual, _ = visual_img.shape
        env_temp = self.main_data['environmental_conditions']['env_temp']

        predictions_list = []
        zoomed_images = []
        target_size = (240, 240)
        
        result_data = results[0]
        model_names = result_data.names

        if result_data.masks is not None:
            for i, (mask, box) in enumerate(zip(result_data.masks, result_data.boxes)):
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                mask_data = mask.data[0].cpu().numpy()
                component_mask_full_res = mask_data[y1:y2, x1:x2]
                resized_mask = cv2.resize(component_mask_full_res, target_size, interpolation=cv2.INTER_NEAREST)
                mask_3channel_bool = np.stack([resized_mask] * 3, axis=-1) > 0
                white_bg = np.full((*target_size, 3), 255, dtype=np.uint8)

                # Imagem visual COM máscara
                cropped_visual = visual_img[y1:y2, x1:x2]
                resized_visual = cv2.resize(cropped_visual, target_size)
                component_visual_isolated = np.where(mask_3channel_bool, resized_visual, white_bg)
                
                # Imagem térmica (continua com máscara)
                thermal_full_resized = cv2.resize(thermal_img, (w_visual, h_visual))
                cropped_thermal = thermal_full_resized[y1:y2, x1:x2]
                resized_thermal = cv2.resize(cropped_thermal, target_size)
                component_thermal_isolated = np.where(mask_3channel_bool, resized_thermal, white_bg)

                zoomed_images.append({
                    "visual": component_visual_isolated,
                    "thermal": component_thermal_isolated
                })

                label = model_names[int(box.cls)]
                temp_max = random.randint(env_temp + 5, env_temp + 30)
                temp_min = temp_max - random.randint(10, 25)
                if temp_min < env_temp: temp_min = env_temp

                predictions_list.append({
                    "id": i + 1, "label": label,
                    "temp_max": temp_max, "temp_min": temp_min,
                })
        
        return zoomed_images, predictions_list

    def add_analysis_to_story(self, story, results, visual_img_path, thermal_img_path, annotated_visual_image_path, temp_dir):
        visual_img = cv2.imread(visual_img_path)
        thermal_img = cv2.imread(thermal_img_path)
        env_temp = self.main_data['environmental_conditions']['env_temp']
        
        zoomed_images, predictions = self._predict_and_process(results, visual_img, thermal_img)
        
        if not predictions: return

        for i, component_assets in enumerate(zoomed_images):
            # Adiciona o título geral da página de análise
            story.append(Paragraph("Relatório de Inspeção Detalhada", self.styles['Title']))
            story.append(Spacer(1, 8*mm))

            # Adiciona a imagem de cena completa
            img_annotated_full = Image(annotated_visual_image_path, width=170*mm, height=127.5*mm, kind='proportional')
            story.append(img_annotated_full)
            story.append(Spacer(1, 5*mm))

            prediction = predictions[i]
            
            # --- Preparação dos Elementos da Tabela ---
            # MODIFICAÇÃO: Tamanho da imagem reduzido para compactar a tabela
            img_size = 0.6 * inch
            comp_visual_path = os.path.join(temp_dir, f"comp_{i+1}_visual.png")
            comp_thermal_path = os.path.join(temp_dir, f"comp_{i+1}_thermal.png")
            cv2.imwrite(comp_visual_path, component_assets["visual"])
            cv2.imwrite(comp_thermal_path, component_assets["thermal"])
            
            img_comp_visual = Image(comp_visual_path, width=img_size, height=img_size)
            img_comp_thermal = Image(comp_thermal_path, width=img_size, height=img_size)

            temp_max = prediction['temp_max']
            temp_min = prediction['temp_min']
            delta_t = temp_max - env_temp
            
            diagnosis_text, diag_color = self.diagnosis_function(prediction['label'], delta_t)
            display_label = self.label_translation.get(prediction['label'], prediction['label'])

            p_temp_amb_key = Paragraph(f"Temperatura ambiente (°C)<br/>(Δt) Temp. máx - Temp. amb", self.styles['Normal'])
            p_temp_amb_val = Paragraph(f"{env_temp:.1f}°C<br/>{delta_t:.1f}°C", self.styles['Normal'])

            # --- Construção da Tabela Unificada ---
            # A primeira linha da tabela já contém o nome específico do componente.
            table_data = [
                [Paragraph(f"<b>{i+1}. {display_label}</b>", self.styles['ComponentTitle']), None, None],
                [img_comp_visual, Paragraph("<b>Análise do Componente</b>", self.styles['h3']), None],
                [None, 'Temperatura máxima', f"{temp_max:.1f}°C"],
                [None, 'Temperatura mínima', f"{temp_min:.1f}°C"],
                [img_comp_thermal, p_temp_amb_key, p_temp_amb_val],
                [None, 'Diagnóstico Preliminar', Paragraph(diagnosis_text, self.styles['Normal'])],
            ]

            comp_table = Table(table_data, colWidths=[1.4*inch, 2.8*inch, 2.8*inch], spaceBefore=10)
            
            comp_table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (2,2), (2,3), 'CENTER'),
                ('ALIGN', (1,4), (2,4), 'CENTER'),
                ('ALIGN', (2,5), (2,5), 'CENTER'),
                ('SPAN', (0,0), (2,0)), 
                ('SPAN', (1,1), (2,1)),
                ('SPAN', (0,1), (0,3)),
                ('SPAN', (0,4), (0,5)),
                ('ALIGN', (0,0), (0,0), 'LEFT'),
                ('LEFTPADDING', (0,0), (0,0), 6),
                ('ALIGN', (1,1), (1,1), 'CENTER'),
                ('BACKGROUND', (1,1), (2,1), colors.lightgrey),
                ('BACKGROUND', (2,5), (2,5), diag_color),
            ]))

            story.append(comp_table)
            story.append(PageBreak())
        
        print("Finished adding component analysis to story with unified table format.")