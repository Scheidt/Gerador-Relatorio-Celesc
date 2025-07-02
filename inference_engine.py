import os
import cv2
from ultralytics import YOLO

class InferenceEngine:
    """
    Encapsula a lógica de carregamento e execução do modelo YOLO.
    Atua como o "Model" na arquitetura, cuidando da lógica de negócio da IA.
    """
    def __init__(self, model_path: str):
        """
        Inicializa o motor de inferência carregando o modelo YOLO.
        O modelo é carregado apenas uma vez para maior eficiência.

        Args:
            model_path (str): Caminho para o arquivo do modelo treinado (.pt).
        """
        print(f"Carregando modelo de: {model_path}")
        self.model = YOLO(model_path)
        print("Modelo carregado com sucesso.")

    def run_inference(self, image_path: str):
        """
        Executa a inferência do modelo na imagem fornecida.

        Args:
            image_path (str): Caminho para a imagem visual a ser analisada.

        Returns:
            list: A lista de resultados da inferência do Ultralytics.
        """
        print(f"Executando inferência em: {image_path}")
        results = self.model(image_path)
        print("Inferência concluída.")
        return results

    def generate_annotated_image(self, results, save_dir: str, filename="annotated_visual.png") -> str:
        """
        Gera e salva a imagem visual com as máscaras e caixas delimitadoras de todos os componentes.

        Args:
            results: O objeto de resultado da inferência do YOLO.
            save_dir (str): O diretório temporário para salvar a imagem.
            filename (str): O nome do arquivo para a imagem anotada.

        Returns:
            str: O caminho completo para a imagem anotada salva.
        """
        if not results:
            print("Nenhum resultado de inferência para gerar imagem anotada.")
            return None
        
        print("Gerando imagem visual anotada...")
        # O método .plot() da Ultralytics retorna a imagem como um array NumPy (BGR)
        annotated_image_np = results[0].plot()
        
        annotated_image_path = os.path.join(save_dir, filename)
        cv2.imwrite(annotated_image_path, annotated_image_np)
        
        print(f"Imagem anotada salva em: {annotated_image_path}")
        return annotated_image_path