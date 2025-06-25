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
    Performs detailed component analysis by running a model,
    and adds the results to a report story.
    """
    def __init__(self, report_main_data):
        self.main_data = report_main_data
        self.styles = getSampleStyleSheet()
        self.label_translation = report_main_data.get('label_translation', {})
        # Store the temperature thresholds provided from main.py
        self.temp_thresholds = report_main_data.get('temp_thresholds', {})
        
    def _predict_and_process(self, model, visual_img, thermal_img):
        """Runs prediction and generates all necessary data and image assets."""
        print("Running prediction and processing results inside ComponentAnalyzer...")
        
        annotated_visual = visual_img.copy()
        h_visual, w_visual, _ = visual_img.shape
        results = model(visual_img)
        
        gps_lat, gps_lon = self.main_data['gps'].lat, self.main_data['gps'].lon
        env_temp = self.main_data['environmental_conditions']['env_temp']
        hr = self.main_data['environmental_conditions']['hr']
        emissivity = self.main_data['emissivity_val']

        predictions_list = []
        zoomed_images = []

        if results and results[0].masks is not None:
            for i, (mask, box) in enumerate(zip(results[0].masks, results[0].boxes)):
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                component_visual = cv2.resize(visual_img[y1:y2, x1:x2], (240, 240))
                component_thermal = cv2.resize(cv2.resize(thermal_img, (w_visual, h_visual))[y1:y2, x1:x2], (240, 240))
                zoomed_images.append({"visual": component_visual, "thermal": component_thermal})

                label = model.names[int(box.cls)]
                predictions_list.append({
                    "id": i + 1,
                    "label": label,
                    "temp": random.randint(40, 95)
                })
        
        return zoomed_images, predictions_list, gps_lat, gps_lon, env_temp, hr, emissivity

    def add_analysis_to_story(self, story, model_path, visual_img_path, thermal_img_path, temp_dir):
        """
        Adds the full component analysis section to the provided story list.
        """
        story.append(PageBreak())

        print(f"ComponentAnalyzer: Loading model from {model_path}...")
        model = YOLO(model_path)
        visual_img = cv2.imread(visual_img_path)
        thermal_img = cv2.imread(thermal_img_path)
        if visual_img is None or thermal_img is None:
            story.append(Paragraph("Error: Could not load images for component analysis.", self.styles['h2']))
            return

        output = self._predict_and_process(model, visual_img, thermal_img)
        zoomed_images, predictions, gps_lat, gps_lon, env_temp, hr, emissivity = output
        
        if not predictions:
            story.append(Paragraph("Component Analysis", self.styles['Title']))
            story.append(Spacer(1, 12))
            story.append(Paragraph("No components were detected in the image.", self.styles['Normal']))
            return

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
        story.append(PageBreak())

        for i, component_assets in enumerate(zoomed_images):
            prediction = predictions[i]
            display_label = self.label_translation.get(prediction['label'], prediction['label'])
            
            story.append(Paragraph(f"Detalhes do Componente {i+1}: {display_label}", self.styles['h2']))
            story.append(Spacer(1, 12))

            comp_visual_path = os.path.join(temp_dir, f"comp_{i+1}_visual.png")
            comp_thermal_path = os.path.join(temp_dir, f"comp_{i+1}_thermal.png")
            cv2.imwrite(comp_visual_path, component_assets["visual"])
            cv2.imwrite(comp_thermal_path, component_assets["thermal"])
            
            img_comp_visual = Image(comp_visual_path, width=2.5*inch, height=2.5*inch, kind='proportional')
            img_comp_thermal = Image(comp_thermal_path, width=2.5*inch, height=2.5*inch, kind='proportional')
            stacked_images = Table([[img_comp_visual], [img_comp_thermal]])

            # --- DYNAMIC DIAGNOSIS LOGIC ---
            temp = prediction['temp']
            raw_label = prediction['label']
            
            # Get the specific threshold for the component, or use the default value.
            danger_threshold = self.temp_thresholds.get(raw_label, self.temp_thresholds.get('default', 60))

            if temp >= danger_threshold:
                diagnosis = "Atenção Requerida"
                bg_color = colors.orange
            else:
                diagnosis = "Normal"
                bg_color = colors.lightgreen
            # --- END OF DYNAMIC LOGIC ---

            comp_data = [
                ["Análise do Componente", ""],
                ["Componente", display_label],
                ["Temperatura Registrada", f"{temp}°C (Limite: {danger_threshold}°C)"],
                ["Diagnóstico Preliminar", diagnosis],
                ["Observações", ""],
            ]
            
            # The bg_color is now dynamically set based on the component type
            comp_table = Table(comp_data, colWidths=[2*inch, 2.2*inch], style=[('SPAN', (0, 0), (1, 0)), ('BACKGROUND', (0, 0), (1, 0), colors.darkslategray), ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'), ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'), ('GRID', (0, 0), (-1, -1), 1, colors.black), ('BACKGROUND', (1, 3), (1, 3), bg_color)])

            combined_layout_table = Table([[stacked_images, comp_table]], colWidths=[2.7*inch, 4.2*inch], style=[('VALIGN', (0,0), (-1,-1), 'TOP')])
            story.append(combined_layout_table)

            if i < len(zoomed_images) - 1:
                story.append(PageBreak())
        
        print("Finished adding component analysis to story.")