import pickle
import cv2
import numpy as np
import ultralytics
import torch

PICKLE_PATH = "pickle_resultado_inferencia.pkl"
THERMAL_IMG_PATH = "Img_Source/Img_Termica.jpg"
VISUAL_IMG_PATH = "Img_Source/Img_Visual.jpg"

def mask_image(SAVE_DIR: str):
    with open(PICKLE_PATH, 'rb') as file:
            response = pickle.load(file)

    # Acessar os resultados da YOLO e as imagens extras
    results = response["resultado"]  # lista de resultados

    thermal_img = cv2.imread(THERMAL_IMG_PATH)
    visual_img = cv2.imread(VISUAL_IMG_PATH)

    # Obtém a imagem com máscaras e bounding boxes desenhados
    image_with_masks = results[0].plot()

    print(f"Dimensões originais:")
    print(f"  image_with_masks: {image_with_masks.shape}")
    print(f"  thermal_img: {thermal_img.shape}")
    print(f"  visual_img: {visual_img.shape}")
    print(f"  Target: {image_with_masks.shape[:2]}")

    # Redimensionar imagens térmica e visual para o mesmo tamanho da imagem com máscara
    target_shape = image_with_masks.shape[:2]
    thermal_img_resized = thermal_img # resize_to_match(thermal_img, target_shape)
    visual_img_resized = visual_img # resize_to_match(visual_img, target_shape)

    # Criar imagem térmica com contornos das máscaras
    thermal_with_contours = thermal_img_resized.copy()

    # Processa as máscaras
    if results[0].masks is not None:
        result = results[0]
        target_shape = result.orig_shape  # (height, width)
        print(f"Dimensões da imagem original: {target_shape}")

        # Obtém as máscaras como numpy arrays
        masks = result.masks.data.cpu().numpy()  # (n_masks, 640, 640)
        print(f"Shape das máscaras originais: {masks.shape}")

        for mask in masks:
            # Redimensionar a máscara para o tamanho da imagem original
            resized_mask = cv2.resize(mask, (target_shape[1], target_shape[0]), interpolation=cv2.INTER_NEAREST)  # (width, height)

            # Converter a máscara para imagem binária 0-255
            mask_uint8 = (resized_mask * 255).astype(np.uint8)

            # Encontrar contornos
            contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # TODO: Usar o contorno p/ fazer imagem nova, colocar fundo branco

            # Desenhar os contornos em vermelho sobre a imagem térmica
            cv2.drawContours(thermal_with_contours, contours, -1, (50, 255, 50), 2)

        print(f"Processamento de contornos concluído para {len(masks)} máscaras.")
    else:
        print("Nenhuma máscara detectada.")

    # Criar visualização final em grade 2x2
    top_row = np.hstack([thermal_img_resized, visual_img_resized])
    bottom_row = np.hstack([thermal_with_contours, image_with_masks])
    final_image = np.vstack([top_row, bottom_row])

    # Salvar resultado
    filename = f"{SAVE_DIR}resultado_final_mascarado.jpg"
    cv2.imwrite(filename, final_image)        
    print(f"Resultado salvo como '{filename}'.")
    return filename