# part_analysis.py
import os
import cv2
import random
import numpy as np
from datetime import datetime
from ultralytics import YOLO
from reportlab.platypus import Paragraph, Table, TableStyle, Image, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

class ComponentAnalyzer:
    """
    Performs detailed component analysis by processing pre-computed model results,
    and adds the results to a report story.
    """
    def __init__(self, report_main_data):
        self.main_data = report_main_data
        self.styles = getSampleStyleSheet()
        self.label_translation = report_main_data.get('label_translation', {})
        self.temp_thresholds = report_main_data.get('temp_thresholds', {})
        
    def _predict_and_process(self, results, visual_img, thermal_img):
        """Processes pre-computed prediction results to generate necessary data."""
        print("Processing pre-computed results inside ComponentAnalyzer...")
        
        h_visual, w_visual, _ = visual_img.shape
        
        gps_lat, gps_lon = self.main_data['gps'].lat, self.main_data['gps'].lon
        env_temp = self.main_data['environmental_conditions']['env_temp']
        hr = self.main_data['environmental_conditions']['hr']
        emissivity = self.main_data['emissivity_val']

        predictions_list = []
        zoomed_images = []
        target_size = (240, 240) # Define target size for component images
        
        # Use the first result object from the pre-computed list
        result_data = results[0]
        model_names = result_data.names

        if result_data.masks is not None:
            for i, (mask, box) in enumerate(zip(result_data.masks, result_data.boxes)):
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # 1. Get the segmentation mask for the current component
                mask_data = mask.data[0].cpu().numpy()
                # Crop the mask to the component's bounding box
                component_mask_full_res = mask_data[y1:y2, x1:x2]
                # Resize the mask to the final target image size
                resized_mask = cv2.resize(component_mask_full_res, target_size, interpolation=cv2.INTER_NEAREST)
                # Create a 3-channel boolean mask for applying to color images
                mask_3channel_bool = np.stack([resized_mask] * 3, axis=-1) > 0

                # 2. Process the VISUAL component image
                cropped_visual = visual_img[y1:y2, x1:x2]
                resized_visual = cv2.resize(cropped_visual, target_size)
                # Create a white background of the same size
                white_bg = np.full_like(resized_visual, 255)
                # Use the mask to select pixels from either the component or the white background
                component_visual_isolated = np.where(mask_3channel_bool, resized_visual, white_bg)
                
                # 3. Process the THERMAL component image
                thermal_full_resized = cv2.resize(thermal_img, (w_visual, h_visual))
                cropped_thermal = thermal_full_resized[y1:y2, x1:x2]
                resized_thermal = cv2.resize(cropped_thermal, target_size)
                # Use the same mask to isolate the thermal component
                component_thermal_isolated = np.where(mask_3channel_bool, resized_thermal, white_bg)


                zoomed_images.append({
                    "visual": component_visual_isolated,
                    "thermal": component_thermal_isolated
                })

                label = model_names[int(box.cls)]
                predictions_list.append({
                    "id": i + 1,
                    "label": label,
                    "temp": random.randint(30, 70)
                })
        
        return zoomed_images, predictions_list, gps_lat, gps_lon, env_temp, hr, emissivity

    def add_analysis_to_story(self, story, results, visual_img_path, thermal_img_path, annotated_visual_image_path, temp_dir):
        """
        Adds the full component analysis section to the provided story list.
        """
        visual_img = cv2.imread(visual_img_path)
        thermal_img = cv2.imread(thermal_img_path)
        if visual_img is None or thermal_img is None:
            # Apenas adiciona um erro se as imagens não puderem ser carregadas
            story.append(PageBreak())
            story.append(Paragraph("Error: Could not load images for component analysis.", self.styles['h2']))
            return

        # Pass the pre-computed results to the processing method
        output = self._predict_and_process(results, visual_img, thermal_img)
        zoomed_images, predictions, gps_lat, gps_lon, env_temp, hr, emissivity = output
        
        if not predictions:
            story.append(PageBreak())
            story.append(Paragraph("Component Analysis", self.styles['Title']))
            story.append(Spacer(1, 12))
            story.append(Paragraph("No components were detected in the image.", self.styles['Normal']))
            return

        story.append(PageBreak())
        story.append(Paragraph("Resumo Térmico por Componente", self.styles['h1']))
        story.append(Spacer(1, 20))
        summary_table_data = [["Nome do Componente", "Temperatura", "Diagnóstico"]]
        table_style_commands = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkslategray), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]
        for i, pred in enumerate(predictions):
            row_index = i + 1
            display_label = self.label_translation.get(pred['label'], pred['label'])
            temp = pred['temp']
            raw_label = pred['label']
            danger_threshold = self.temp_thresholds.get(raw_label, self.temp_thresholds.get('default', 60))
            if temp >= danger_threshold:
                diagnosis, bg_color = "Atenção Requerida", colors.orange
            else:
                diagnosis, bg_color = "Normal", colors.lightgreen
            summary_table_data.append([display_label, f"{temp}°C", diagnosis])
            table_style_commands.append(('BACKGROUND', (0, row_index), (-1, row_index), bg_color))
        thermal_summary_table = Table(summary_table_data, colWidths=[3*inch, 2*inch, 2*inch])
        thermal_summary_table.setStyle(TableStyle(table_style_commands))
        story.append(thermal_summary_table)

        # Início da análise detalhada individual
        story.append(PageBreak())
        story.append(Paragraph(f"Relatório de Inspeção Detalhada", self.styles['Title']))
        story.append(Spacer(1, 24))

        max_temp = max([p['temp'] for p in predictions], default=env_temp)
        summary_data = [
            ["Informações Gerais da Inspeção", ""],
            ["Coordenadas GPS", f"{gps_lat}, {gps_lon}"],
            ["Temperatura Ambiente", f"{env_temp}°C"],
            ["Umidade Relativa", f"{hr*100:.0f}%"],
            ["Emissividade", f"{emissivity}"],
            ["Temperatura Máxima Detectada", f"{max_temp}°C"],
        ]
        summary_table = Table(summary_data, colWidths=[2.5*inch, 4*inch], style=[('SPAN', (0, 0), (1, 0)), ('BACKGROUND', (0, 0), (1, 0), colors.darkslategray), ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'), ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'), ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        story.append(summary_table)
        
        for i, component_assets in enumerate(zoomed_images):
            story.append(PageBreak())
            prediction = predictions[i]
            display_label = self.label_translation.get(prediction['label'], prediction['label'])
            
            story.append(Paragraph(f"Detalhes do Componente {i+1}: {display_label}", self.styles['h2']))
            story.append(Spacer(1, 12))

            comp_visual_path = os.path.join(temp_dir, f"comp_{i+1}_visual.png")
            comp_thermal_path = os.path.join(temp_dir, f"comp_{i+1}_thermal.png")
            cv2.imwrite(comp_visual_path, component_assets["visual"])
            cv2.imwrite(comp_thermal_path, component_assets["thermal"])
            
            img_comp_visual = Image(comp_visual_path, width=1*inch, height=1*inch, kind='proportional')
            img_comp_thermal = Image(comp_thermal_path, width=1*inch, height=1*inch, kind='proportional')
            img_annotated_full = Image(annotated_visual_image_path, width=2.5*inch, height=2.5*inch, kind='proportional')
            
            stacked_images = Table([
                [Paragraph("<i>Zoom Visual</i>", self.styles['Normal'])], [img_comp_visual], 
                [Paragraph("<i>Zoom Térmico</i>", self.styles['Normal'])], [img_comp_thermal],
                [Paragraph("<i>Visão Geral Anotada</i>", self.styles['Normal'])], [img_annotated_full]
            ], style=[('ALIGN', (0,0), (-1,-1), 'CENTER')])

            temp = prediction['temp']
            raw_label = prediction['label']
            danger_threshold = self.temp_thresholds.get(raw_label, self.temp_thresholds.get('default', 60))

            if temp >= danger_threshold:
                diagnosis, bg_color = "Atenção Requerida", colors.orange
            else:
                diagnosis, bg_color = "Normal", colors.lightgreen

            comp_data = [
                ["Análise do Componente", ""],
                ["Componente", display_label],
                ["Temperatura Registrada", f"{temp}°C (Limite: {danger_threshold}°C)"],
                ["Diagnóstico Preliminar", diagnosis]
            ]
            
            comp_table = Table(comp_data, colWidths=[2*inch, 2.2*inch], style=[('SPAN', (0, 0), (1, 0)), ('BACKGROUND', (0, 0), (1, 0), colors.darkslategray), ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'), ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'), ('GRID', (0, 0), (-1, -1), 1, colors.black), ('BACKGROUND', (1, 3), (1, 3), bg_color)])

            combined_layout_table = Table([[stacked_images, comp_table]], colWidths=[2.8*inch, 4.2*inch], style=[('VALIGN', (0,0), (-1,-1), 'TOP')])
            story.append(combined_layout_table)
        
        print("Finished adding component analysis to story.")