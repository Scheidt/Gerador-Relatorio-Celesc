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


from ultralytics import YOLO
model = YOLO("/app/docker_server/weights/best_simplified.onnx", task="segment")

label_translation = {
    "transformer" : "Transformador",
    "vertical-insulator" : "Isolador vertical",
    "horizontal-insulator" : "Isolador horizontal",
    "fuse-cutout" : "Chave fusivel",
    "overhead-switch" : "Chave faca",
    "connector" : "Conector"
}

SAVE_DIR = "/app/fotos_docker/"


def create_description_text(gps, temp=25, hr=0.65, emissivity=0.7):
    dt = datetime.now().strftime('%d/%m/%y %H:%M')
    #return f"GPS {gps.lat} {gps.lon}\n{dt}\nT: {temp}\N{DEGREE SIGN}C HR: {hr} \u03B5: {emissivity}"
    return f"GPS {gps.lat} {gps.lon}\n{dt}\nT: {temp}C HR: {hr} e: {emissivity}"

class GPS:
    def __init__(self,lat, lon):
        self.lat = lat
        self.lon = lon
        
def predict_and_present(image_visual, image_thermal, results, plot=False):
    # Load images
    #image_visual = cv2.imread(image_path_visual)
    #image_thermal = cv2.imread(image_path_thermal)

    # Create copies of the original images
    original_copy_thermal = image_thermal.copy()
    original_copy_visual = image_visual.copy()

    # Get original image dimensions
    original_width_visual = original_copy_visual.shape[1]  # Width of the visual image
    original_height_visual = original_copy_visual.shape[0]  # Height of the visual image
    original_width_thermal = original_copy_thermal.shape[1]  # Width of the thermal image
    original_height_thermal = original_copy_thermal.shape[0]  # Height of the thermal image

    # Calculate scaling factors
    scale_x = 1 # original_width_thermal / original_width_visual
    scale_y = 1 # original_height_thermal / original_height_visual

    # Make predictions
    #results = model(image_visual)
    neon_green = (0, 255, 0)  # Define neon green color (BGR format)

    # List to store predictions
    predictions_list = []
    zoomed_images = []  # List to store zoomed images

    # Get masks and boxes
    masks = results[0].masks
    boxes = results[0].boxes

    # Crop and resize the component
    component_image_size = (240, 240)

    gps = GPS(10,-23)
    hr=0.6
    emissivity=0.7
    env_temp=25


    # Draw segmentation masks and bounding boxes
    if masks is not None:
        for j, (mask, box) in enumerate(zip(masks, boxes)):
            # Get the label and confidence
            label = model.names[int(box.cls)]
            confidence = float(box.conf)

            # Original coordinates
            # boundind box do componente
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Scale the coordinates
            # bounding box nas novas coordenadas
            x1_new = int(x1 * scale_x)
            y1_new = int(y1 * scale_y)
            x2_new = int(x2 * scale_x)
            y2_new = int(y2 * scale_y)

            # resize na termica para tamanho da visual
            component = cv2.resize(original_copy_thermal, (original_width_visual, original_height_visual))[y1:y2, x1:x2]
            # retirando o componente na visual
            component_visual = cv2.resize(original_copy_visual[y1:y2, x1:x2], component_image_size)
            component = cv2.resize(component, component_image_size)

            # Draw the segmentation mask
            mask = mask.data[0].cpu().numpy()
            # use this one when adding the countour in the thermal image
            #mask_resized = cv2.resize(mask, (original_width_thermal, original_height_thermal))
            
            result = results[0]
            target_shape = result.orig_shape  # (height, width)
            resized_mask = cv2.resize(mask, (target_shape[1], target_shape[0]), interpolation=cv2.INTER_NEAREST)  # (width, height)
            contours, _ = cv2.findContours(resized_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            #contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(image_visual, contours, -1, neon_green, 2)

            # Add enumeration number
            # coloca o numero do componetne na imagem térmica
            cv2.putText(image_thermal, str(j + 1), (x1_new, y2_new + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.25, neon_green, 1)
            # coloca o numero do componetne na imagem visual
            cv2.putText(image_visual, str(j + 1), (x1, y2 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, neon_green, 2)


            # Add label and temperature to the zoomed component thermal and visual
            temperature = random.randint(15, 80)
            cv2.putText(component, f"{str(j + 1)}: {label_translation[label]} {temperature}C", (5, component_image_size[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, neon_green, 1)
            cv2.putText(component_visual, f"{str(j + 1)}: {label_translation[label]} {temperature}C", (5, component_image_size[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, neon_green, 1)

            # Append prediction to the list
            predictions_list.append({
                "id": j + 1,
                "label": label,
                "confidence": confidence,
                "position": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                "temp": temperature
            })
            zoomed_images.append({"thermal": component, "visual" : component_visual})

    # Add description text
    description_text = create_description_text(gps, env_temp, hr, emissivity)
    y0 = original_height_thermal - 8
    dy = -10
    for i, line in enumerate(description_text.split('\n')):
        y = y0 + i * dy
        cv2.putText(image_thermal, line, (0, int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 255, 255), 1)

    # Add predictions text at the bottom
    y0 = original_height_visual - 10
    dy = 20
    for i, prediction in enumerate(reversed(predictions_list)):
        text = f"{prediction['id']}: {label_translation[prediction['label']]} {prediction['temp']}C"
        cv2.putText(image_visual, text, (0, int(y0 - i * dy)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, neon_green, 2)

    # Display the image using matplotlib
    if plot:
        plt.imshow(cv2.cvtColor(image_thermal, cv2.COLOR_BGR2RGB))  # Convert BGR to RGB for matplotlib
        plt.axis('off')  # Hide the axes
        plt.show()

        plt.imshow(cv2.cvtColor(image_visual, cv2.COLOR_BGR2RGB))  # Convert BGR to RGB for matplotlib
        plt.axis('off')  # Hide the axes
        plt.show()

        for component in zoomed_images:
            for image_type in ["thermal", "visual"]:
                plt.imshow(cv2.cvtColor(component[image_type], cv2.COLOR_BGR2RGB))  # Convert BGR to RGB for matplotlib
                plt.axis('off')  # Hide the axes
                plt.show()

    return image_thermal, image_visual, zoomed_images, predictions_list, gps, hr, emissivity, env_temp

def create_pdf_report(output, output_pdf_path):
    # Unpack the output
    image_thermal, image_visual, zoomed_images, predictions_list, gps, hr, emissivity, env_temp = output

    # Create a PDF document
    pdf = SimpleDocTemplate(output_pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Add title
    title = Paragraph(f"Relatório de inspeção nº X - {datetime.now().strftime('%d/%m/%y %H:%M')}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))

    # Add images side by side
    img_thermal_path = f"{SAVE_DIR}temp_thermal.png"
    img_visual_path = f"{SAVE_DIR}temp_visual.png"
    cv2.imwrite(img_thermal_path, image_thermal)
    cv2.imwrite(img_visual_path, image_visual)

    img_thermal = Image(img_thermal_path, width=3 * inch, height=3 * inch)
    img_visual = Image(img_visual_path, width=3 * inch, height=3 * inch)

    # Create a table to place images side by side
    img_table = Table([[img_visual, img_thermal]], colWidths=[3 * inch, 3 * inch])
    img_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(img_table)
    story.append(Spacer(1, 12))

    # Add summary table
    summary_data = [
        ["Informações detalhadas", ""],
        ["GPS", f"{gps.lat}, {gps.lon}"],
        ["Temperatura ambiente", f"{env_temp}°C"],
        ["Umidade relativa", f"{hr*100}%"],
        ["Emissividade", f"{emissivity}"],
        ["Temperatura máxima", f"{max(p['temp'] for p in predictions_list)}°C"],
    ]

    # Get address from Google Maps API
    try:
        response = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?latlng={gps.lat},{gps.lon}&key=YOUR_GOOGLE_MAPS_API_KEY")
        address = response.json()['results'][0]['formatted_address']
    except:
        address = "-"
    summary_data.append(["Endereço", address])

    summary_table = Table(summary_data, colWidths=[2 * inch, 4 * inch])
    summary_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),  # Mescla a primeira linha
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(summary_table)
    story.append(PageBreak())

    # Add zoomed components
    for i, component in enumerate(zoomed_images):
        story.append(Paragraph(f"Componente {i + 1} - {label_translation[predictions_list[i]['label']]}", styles['Heading2']))
        img_thermal_path = f"{SAVE_DIR}temp_thermal_component_{i + 1}.png"
        img_visual_path = f"{SAVE_DIR}temp_visual_component_{i + 1}.png"
        cv2.imwrite(img_thermal_path, component["thermal"])
        cv2.imwrite(img_visual_path, component["visual"])

        img_thermal = Image(img_thermal_path, width=3 * inch, height=3 * inch)
        img_visual = Image(img_visual_path, width=3 * inch, height=3 * inch)

        # Create a table to place images side by side
        img_table = Table([[img_visual, img_thermal]], colWidths=[3 * inch, 3 * inch])
        img_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(img_table)
        story.append(Spacer(1, 12))

        # Add component details
        component_data = [
            ["Informações detalhadas", ""],
            ["Componente", label_translation[predictions_list[i]["label"]]],
            ["Temperatura", f"{predictions_list[i]['temp']}°C"],
            ["Manutenção", f""],
            #["Confidence", f"{predictions_list[i]['confidence']:.2f}"],
        ]
        component_table = Table(component_data, colWidths=[2 * inch, 4 * inch])
        component_table.setStyle(TableStyle([
            ('SPAN', (0, 0), (1, 0)),  # Mescla a primeira linha
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(component_table)
        story.append(PageBreak())

    # Build the PDF
    pdf.build(story)

    # Clean up temporary files
    #import os
    #os.remove(img_thermal_path)
    #os.remove(img_visual_path)
    #for i in range(len(zoomed_images)):
    #    os.remove(f"temp_thermal_component_{i + 1}.png")
    #    os.remove(f"temp_visual_component_{i + 1}.png")