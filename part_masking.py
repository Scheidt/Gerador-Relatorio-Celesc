from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
import matplotlib.pyplot as plt
from datetime import datetime
import random
import os
import cv2
import numpy as np

# It's better to load the model once if you are processing multiple images,
# but for a self-contained function, we can load it inside.
# from ultralytics import YOLO

# This is a placeholder since the original code loads a model.
# In a real scenario, this would be your YOLO model object.
# model = YOLO("/path/to/your/model.pt", task="segment")

label_translation = {
    "transformer" : "Transformador",
    "vertical-insulator" : "Isolador vertical",
    "horizontal-insulator" : "Isolador horizontal",
    "fuse-cutout" : "Chave fusivel",
    "overhead-switch" : "Chave faca",
    "connector" : "Conector"
}

# Define a temporary save directory for images
SAVE_DIR = "./temp_report_images/"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

class GPS:
    """A simple class to hold GPS coordinates."""
    def __init__(self,lat, lon):
        self.lat = lat
        self.lon = lon

def create_description_text(gps, temp=25, hr=0.65, emissivity=0.7):
    """Creates the description text for the thermal image."""
    dt = datetime.now().strftime('%d/%m/%y %H:%M')
    return f"GPS {gps.lat} {gps.lon}\n{dt}\nT: {temp}C HR: {hr} e: {emissivity}"

def predict_and_present(model, image_visual, image_thermal, plot=False):
    """
    Runs prediction, draws masks and boxes, and prepares data for the report.
    Note: This is an adapted version of your original function.
    """
    # Create copies of the original images
    original_copy_thermal = image_thermal.copy()
    original_copy_visual = image_visual.copy()

    # Get original image dimensions
    original_height_visual, original_width_visual, _ = original_copy_visual.shape
    original_height_thermal, original_width_thermal, _ = original_copy_thermal.shape

    # Make predictions
    results = model(image_visual)
    neon_green = (0, 255, 0)  # Define neon green color (BGR format)

    # List to store predictions and zoomed images
    predictions_list = []
    zoomed_images = []
    component_image_size = (240, 240)

    # Mock data for demonstration purposes, as it was in the original file
    gps = GPS(-27.59, -48.54) # Example coordinates for Florianópolis
    hr=0.6
    emissivity=0.7
    env_temp=25

    # Process masks and boxes from the model results
    if results and results[0].masks is not None:
        masks = results[0].masks
        boxes = results[0].boxes

        for j, (mask, box) in enumerate(zip(masks, boxes)):
            label = model.names[int(box.cls)]
            
            # Bounding box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Crop the component from the thermal and visual images
            component_thermal = cv2.resize(original_copy_thermal, (original_width_visual, original_height_visual))[y1:y2, x1:x2]
            component_visual_original = original_copy_visual[y1:y2, x1:x2]

            # Resize them for the report
            component_thermal = cv2.resize(component_thermal, component_image_size)
            component_visual = cv2.resize(component_visual_original, component_image_size)

            # Draw contours on the main visual image
            mask_data = mask.data[0].cpu().numpy()
            target_shape = results[0].orig_shape
            resized_mask = cv2.resize(mask_data, (target_shape[1], target_shape[0]), interpolation=cv2.INTER_NEAREST)
            contours, _ = cv2.findContours(resized_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(image_visual, contours, -1, neon_green, 2)

            # Add enumeration number to the main images
            cv2.putText(image_thermal, str(j + 1), (x1, y2 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, neon_green, 1)
            cv2.putText(image_visual, str(j + 1), (x1, y2 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, neon_green, 2)

            # Add text to the cropped component images
            temperature = random.randint(15, 80) # Using random temp as in original
            info_text = f"{j + 1}: {label_translation.get(label, label)} {temperature}C"
            cv2.putText(component_thermal, info_text, (5, component_image_size[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, neon_green, 1)
            cv2.putText(component_visual, info_text, (5, component_image_size[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, neon_green, 1)

            predictions_list.append({
                "id": j + 1,
                "label": label,
                "temp": temperature
            })
            zoomed_images.append({"thermal": component_thermal, "visual": component_visual})

    # Add description text to thermal image
    description_text = create_description_text(gps, env_temp, hr, emissivity)
    y0 = original_height_thermal - 15
    for i, line in enumerate(description_text.split('\n')):
        y = y0 - i * 20
        cv2.putText(image_thermal, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return image_thermal, image_visual, zoomed_images, predictions_list, gps, hr, emissivity, env_temp


def add_inspection_to_story(model_path, visual_img_path, thermal_img_path, story):
    """
    Processes inspection data and adds all PDF report elements to a story.

    Args:
        model_path (str): The file path to the YOLO model (.pt, .onnx, etc.).
        visual_img_path (str): The file path to the visual image.
        thermal_img_path (str): The file path to the thermal image.
        story (list): The reportlab story list to append elements to.

    Returns:
        list: The updated story list with new report elements.
    """
    # Import YOLO here to avoid making it a hard dependency for the whole file
    from ultralytics import YOLO

    # --- 1. Load Model and Images ---
    print(f"Loading model from {model_path}...")
    model = YOLO(model_path)
    
    print(f"Loading images: {visual_img_path}, {thermal_img_path}...")
    visual_img = cv2.imread(visual_img_path)
    thermal_img = cv2.imread(thermal_img_path)
    
    if visual_img is None or thermal_img is None:
        print("Error: Could not load one or both images.")
        return story

    # --- 2. Run Prediction and Image Processing ---
    print("Running prediction and processing results...")
    output = predict_and_present(model, visual_img, thermal_img)
    image_thermal, image_visual, zoomed_images, predictions_list, gps, hr, emissivity, env_temp = output

    # --- 3. Generate PDF Elements and Add to Story ---
    print("Generating PDF elements...")
    styles = getSampleStyleSheet()
    
    # Add title
    story.append(Paragraph(f"Relatório de Inspeção - {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Title']))
    story.append(Spacer(1, 12))

    # Add main images side by side
    img_thermal_path = os.path.join(SAVE_DIR, "temp_thermal_main.png")
    img_visual_path = os.path.join(SAVE_DIR, "temp_visual_main.png")
    cv2.imwrite(img_thermal_path, image_thermal)
    cv2.imwrite(img_visual_path, image_visual)

    img_thermal_report = Image(img_thermal_path, width=3*inch, height=3*inch, kind='proportional')
    img_visual_report = Image(img_visual_path, width=3*inch, height=3*inch, kind='proportional')

    img_table = Table([[img_visual_report, img_thermal_report]], colWidths=[3.2*inch, 3.2*inch])
    story.append(img_table)
    story.append(Spacer(1, 24))

    # Add summary table
    max_temp = max([p['temp'] for p in predictions_list], default=env_temp)
    summary_data = [
        ["Informações Gerais da Inspeção", ""],
        ["Coordenadas GPS", f"{gps.lat}, {gps.lon}"],
        ["Temperatura Ambiente", f"{env_temp}°C"],
        ["Umidade Relativa", f"{hr*100:.0f}%"],
        ["Emissividade", f"{emissivity}"],
        ["Temperatura Máxima Detectada", f"{max_temp}°C"],
    ]
    summary_table = Table(summary_data, colWidths=[2.5*inch, 4*inch])
    summary_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 0), (1, 0), colors.darkslategray),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(summary_table)
    story.append(PageBreak())

    # Add detailed sections for each detected component
    for i, component in enumerate(zoomed_images):
        prediction = predictions_list[i]
        label = label_translation.get(prediction['label'], prediction['label'])
        
        story.append(Paragraph(f"Detalhes do Componente {i+1}: {label}", styles['h2']))
        story.append(Spacer(1, 12))

        # Save and add component images
        comp_thermal_path = os.path.join(SAVE_DIR, f"comp_{i+1}_thermal.png")
        comp_visual_path = os.path.join(SAVE_DIR, f"comp_{i+1}_visual.png")
        cv2.imwrite(comp_thermal_path, component["thermal"])
        cv2.imwrite(comp_visual_path, component["visual"])
        
        img_comp_thermal = Image(comp_thermal_path, width=3*inch, height=3*inch, kind='proportional')
        img_comp_visual = Image(comp_visual_path, width=3*inch, height=3*inch, kind='proportional')
        
        comp_img_table = Table([[img_comp_visual, img_comp_thermal]], colWidths=[3.2*inch, 3.2*inch])
        story.append(comp_img_table)
        story.append(Spacer(1, 12))

        # Add component details table
        component_data = [
            ["Análise do Componente", ""],
            ["Componente", label],
            ["Temperatura Registrada", f"{prediction['temp']}°C"],
            ["Diagnóstico Preliminar", "Normal" if prediction['temp'] < 60 else "Atenção Requerida"],
            ["Observações", ""],
        ]
        comp_table = Table(component_data, colWidths=[2.5*inch, 4*inch])
        comp_table.setStyle(TableStyle([
            ('SPAN', (0, 0), (1, 0)),
            ('BACKGROUND', (0, 0), (1, 0), colors.darkslategray),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            # Set background color based on temperature
            ('BACKGROUND', (1, 2), (1, 2), colors.orange if prediction['temp'] >= 60 else colors.lightgreen),
        ]))
        story.append(comp_table)
        
        # Add a page break if it's not the last component
        if i < len(zoomed_images) - 1:
            story.append(PageBreak())

    print("Finished generating PDF elements.")
    # --- 4. Return the updated story ---
    return story


# --- EXAMPLE USAGE ---
"""
if __name__ == '__main__':
    # You need to have 'ultralytics' and 'reportlab' installed
    # pip install ultralytics reportlab
    
    # Also, create placeholder images or use your own.
    # We will create blank images for this example to run.
    if not os.path.exists("visual_example.png"):
        cv2.imwrite("visual_example.png", np.zeros((640, 640, 3), dtype=np.uint8))
    if not os.path.exists("thermal_example.png"):
        cv2.imwrite("thermal_example.png", np.zeros((640, 640, 3), dtype=np.uint8))

    # --- Step 1: Initialize Reportlab Document ---
    output_pdf_path = "complete_inspection_report.pdf"
    pdf = SimpleDocTemplate(output_pdf_path, pagesize=A4)
    story = []

    # --- Step 2: Define paths ---
    # NOTE: You MUST replace this with a valid path to your model file.
    # For this example, we point to the standard yolov8n-seg.pt model.
    # It will be downloaded automatically by ultralytics if not present.
    model_file = "yolov8n-seg.pt" 
    visual_image = "visual_example.png"
    thermal_image = "thermal_example.png"

    # --- Step 3: Call the function to populate the story ---
    # The function will run the model and add all pages/elements to the story
    story = add_inspection_to_story(model_file, visual_image, thermal_image, story)

    # --- Step 4: Build the PDF ---
    if story:
        print(f"Building PDF... -> {output_pdf_path}")
        pdf.build(story)
        print("PDF built successfully.")
    else:
        print("Story is empty, PDF not generated.")
        
    # --- Optional: Clean up temporary files ---
    # import shutil
    # if os.path.exists(SAVE_DIR):
    #     shutil.rmtree(SAVE_DIR)
"""