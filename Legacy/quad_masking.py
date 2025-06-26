import pickle
import cv2
import numpy as np
import ultralytics
import torch

def quad_masked_image(pickle_path: str, thermal_img_path: str, visual_img_path: str, save_dir: str):
    """
    Generates a 2x2 image grid with original, annotated, and contoured images.

    Args:
        pickle_path (str): Path to the pickle file containing YOLO inference results.
        thermal_img_path (str): Path to the source thermal image.
        visual_img_path (str): Path to the source visual image.
        save_dir (str): Directory where the output image will be saved.

    Returns:
        str: The path to the generated image.
    """
    with open(pickle_path, 'rb') as file:
            response = pickle.load(file)

    # Acessar os resultados da YOLO e as imagens extras
    results = response["resultado"]  # lista de resultados

    thermal_img = cv2.imread(thermal_img_path)
    visual_img = cv2.imread(visual_img_path)

    # Obtém a imagem com máscaras e bounding boxes desenhados
    image_with_masks = results[0].plot()

    print(f"Dimensões originais:")
    print(f"  image_with_masks: {image_with_masks.shape}")
    print(f"  thermal_img: {thermal_img.shape}")
    print(f"  visual_img: {visual_img.shape}")
    print(f"  Target: {image_with_masks.shape[:2]}")

    # Redimensionar imagens térmica e visual para o mesmo tamanho da imagem com máscara
    target_shape = image_with_masks.shape[:2]
    thermal_img_resized = cv2.resize(thermal_img, (target_shape[1], target_shape[0]))
    visual_img_resized = cv2.resize(visual_img, (target_shape[1], target_shape[0]))

    # Criar imagem térmica com contornos das máscaras
    thermal_with_contours = thermal_img_resized.copy()

    # Processa as máscaras
    if results[0].masks is not None:
        result = results[0]
        # Use a forma da imagem plotada que já está no tamanho correto
        plot_shape = image_with_masks.shape
        print(f"Dimensões da imagem de destino (plot): {plot_shape}")

        # Obtém as máscaras como numpy arrays
        masks = result.masks.data.cpu().numpy()
        print(f"Shape das máscaras originais: {masks.shape}")

        for mask in masks:
            # Redimensionar a máscara para o tamanho da imagem de destino (plot)
            resized_mask = cv2.resize(mask, (plot_shape[1], plot_shape[0]), interpolation=cv2.INTER_NEAREST)

            # Converter a máscara para imagem binária 0-255
            mask_uint8 = (resized_mask * 255).astype(np.uint8)

            # Encontrar contornos
            contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Desenhar os contornos em verde sobre a imagem térmica
            cv2.drawContours(thermal_with_contours, contours, -1, (50, 255, 50), 2)

        print(f"Processamento de contornos concluído para {len(masks)} máscaras.")
    else:
        print("Nenhuma máscara detectada.")

    # Criar visualização final em grade 2x2
    top_row = np.hstack([thermal_img_resized, visual_img_resized])
    bottom_row = np.hstack([thermal_with_contours, image_with_masks])
    final_image = np.vstack([top_row, bottom_row])

    # Salvar resultado
    filename = f"{save_dir}/resultado_final_mascarado.jpg"
    cv2.imwrite(filename, final_image)
    print(f"Resultado salvo como '{filename}'.")
    return filename