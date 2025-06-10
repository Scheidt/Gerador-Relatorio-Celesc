import socket
import pickle
import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import predict_and_present
from utils import create_pdf_report

SERVER_HOST = "0.0.0.0"  # IP do servidor (pode ser 127.0.0.1 se o cliente e servidor estiverem na mesma máquina)
SERVER_PORT = 6000  # Porta de comunicação

# Diretório para salvar as imagens
SAVE_DIR = "/app/resultado_final/"
SAVE_DIR_PDF = "/app/relatorios/"

# Criar socket para receber dados
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_HOST, SERVER_PORT))
server.listen(5)

# Garantir que todas as imagens tenham o mesmo tamanho
def resize_to_match(image, target_shape):
    return cv2.resize(image, (target_shape[1], target_shape[0]))  # (width, height)

while True:
    try:
        conn, addr = server.accept()
        with conn:
            print(f"Conectado a {addr}")

            # Receber os dados pickle
            data = b""
            while True:
                packet = conn.recv(4096)  # Tamanho do buffer
                if not packet:
                    break
                data += packet

            # Desserializar os dados recebidos
            response = pickle.loads(data)
            print("Pickle recebido e carregado!")

            # Acessar os resultados da YOLO e as imagens extras
            results = response["results"]  # lista de resultados
            thermal_img = response["thermal"]
            visual_img = response["visual"]

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
                    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
            filename = f"{SAVE_DIR}resultado_final_{response['timestamp']}.jpg"
            cv2.imwrite(filename, final_image)        
            print(f"Resultado salvo como '{filename}'.")


            output = predict_and_present(visual_img, thermal_img, results, plot=False)
            create_pdf_report(output, f"{SAVE_DIR_PDF}inspection_report_{response['timestamp']}.pdf")
            print(f"Relatorio final gerado e salvo em: {SAVE_DIR_PDF}inspection_report_{response['timestamp']}.pdf")
    
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário (Ctrl+C).")
        break
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        print("ERRO: Reiniciando o loop de geração de resultados")
