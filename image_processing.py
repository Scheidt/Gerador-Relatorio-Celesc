# image_processing.py
import cv2
import numpy as np
from datetime import datetime
import random
from ultralytics import YOLO

# Label translations are kept here as they are specific to the model's output
LABEL_TRANSLATION = {
    "transformer" : "Transformador",
    "vertical-insulator" : "Isolador vertical",
    "horizontal-insulator" : "Isolador horizontal",
    "fuse-cutout" : "Chave fusivel",
    "overhead-switch" : "Chave faca",
    "connector" : "Conector"
}

class GPS:
    """A simple class to hold GPS coordinates."""
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

def _create_description_text(gps, temp=25, hr=0.65, emissivity=0.7):
    """Creates the description text for the thermal image."""
    dt = datetime.now().strftime('%d/%m/%y %H:%M')
    return f"GPS {gps.lat} {gps.lon}\n{dt}\nT: {temp}C HR: {hr} e: {emissivity}"

def analyze_images(model_path, visual_img_path, thermal_img_path):
    """
    Loads model and images, runs prediction, annotates images,
    and returns all processed data.

    Args:
        model_path (str): Path to the YOLO model.
        visual_img_path (str): Path to the visual image.
        thermal_img_path (str): Path to the thermal image.

    Returns:
        dict: A dictionary containing all processed images and extracted data.
    """
    print("Loading model and images...")
    model = YOLO(model_path)
    image_visual = cv2.imread(visual_img_path)
    image_thermal = cv2.imread(thermal_img_path)

    if image_visual is None or image_thermal is None:
        raise FileNotFoundError(f"Could not load one or both images. Check paths: {visual_img_path}, {thermal_img_path}")

    original_copy_thermal = image_thermal.copy()
    original_copy_visual = image_visual.copy()
    h_visual, w_visual, _ = original_copy_visual.shape
    
    print("Running model prediction...")
    results = model(image_visual)
    
    # --- Prepare for data extraction ---
    predictions_list = []
    zoomed_images = []
    component_image_size = (240, 240)
    neon_green = (0, 255, 0)

    # Mock data for environmental conditions. This could be passed in later.
    gps = GPS(-27.59, -48.54) # Florianópolis coordinates
    hr = 0.6
    emissivity = 0.7
    env_temp = 25

    if results and results[0].masks is not None:
        print(f"Found {len(results[0].masks)} components. Processing...")
        for i, (mask, box) in enumerate(zip(results[0].masks, results[0].boxes)):
            label = model.names[int(box.cls)]
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Draw segmentation contours on the main visual image
            mask_data = mask.data[0].cpu().numpy()
            resized_mask = cv2.resize(mask_data, (w_visual, h_visual), interpolation=cv2.INTER_NEAREST)
            contours, _ = cv2.findContours(resized_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(image_visual, contours, -1, neon_green, 2)

            # Add enumeration number to both main images
            cv2.putText(image_visual, str(i + 1), (x1, y2 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, neon_green, 2)
            cv2.putText(image_thermal, str(i + 1), (x1, y2 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, neon_green, 1)

            # Crop, resize, and annotate components for detailed view
            component_visual = cv2.resize(original_copy_visual[y1:y2, x1:x2], component_image_size)
            component_thermal = cv2.resize(cv2.resize(original_copy_thermal, (w_visual, h_visual))[y1:y2, x1:x2], component_image_size)
            
            temperature = random.randint(15, 80) # Mock temperature
            info_text = f"{i + 1}: {LABEL_TRANSLATION.get(label, label)} {temperature}C"
            cv2.putText(component_visual, info_text, (5, component_image_size[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, neon_green, 1)
            cv2.putText(component_thermal, info_text, (5, component_image_size[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, neon_green, 1)

            predictions_list.append({"id": i + 1, "label": label, "temp": temperature})
            zoomed_images.append({"thermal": component_thermal, "visual": component_visual})

    # Add environmental data text to the main thermal image
    h_thermal, _, _ = image_thermal.shape
    description_text = _create_description_text(gps, env_temp, hr, emissivity)
    y0 = h_thermal - 15
    for i, line in enumerate(description_text.split('\n')):
        y = y0 - i * 20
        cv2.putText(image_thermal, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
    print("Image analysis complete.")
    
    return {
        "annotated_visual": image_visual,
        "annotated_thermal": image_thermal,
        "zoomed_components": zoomed_images,
        "predictions": predictions_list,
        "gps": gps,
        "humidity": hr,
        "emissivity": emissivity,
        "env_temp": env_temp,
        "max_detected_temp": max([p['temp'] for p in predictions_list], default=env_temp)
    }