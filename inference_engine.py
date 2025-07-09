import os
import cv2
import pickle
from ultralytics import YOLO

class InferenceEngine:
    """
    Encapsula a lógica de carregamento de resultados de inferência e a geração de imagens.
    Atua como o "Model" na arquitetura, cuidando da lógica de negócio da IA.
    """
    def __init__(self):
        """
        Inicializa o motor de inferência. O modelo não é mais carregado aqui.
        """
        print("Motor de inferência inicializado. Pronto para carregar resultados.")

    def load_inference_from_pickle(self, pickle_path: str):
        """
        Carrega os resultados da inferência de um arquivo .pkl.

        Args:
            pickle_path (str): Caminho para o arquivo .pkl com os resultados.

        Returns:
            list: A lista de resultados da inferência do Ultralytics.
        """
        print(f"Carregando resultados da inferência de: {pickle_path}")
        if not os.path.exists(pickle_path):
            raise FileNotFoundError(f"Arquivo pickle não encontrado: {pickle_path}")
        
        with open(pickle_path, 'rb') as f:
            data = pickle.load(f)
            # O resultado está sob a chave 'resultado' conforme a estrutura fornecida
            results = data['resultado']
        
        print("Resultados da inferência carregados com sucesso.")
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