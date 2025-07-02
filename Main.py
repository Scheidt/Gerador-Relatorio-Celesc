import tempfile
import pickle
import os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, PageBreak, Image, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from ultralytics import YOLO
from inference_engine import *

# --- Local Imports ---
from report_generator import ReportGenerator
from part_analysis import ComponentAnalyzer


# --- Data Structures ---
class GPS:
    """A simple class to hold GPS coordinates."""
    def __init__(self, lat, lon): self.lat = lat; self.lon = lon

# --- All Data Generation Functions ---
IMG_FOLDER = 'Img_Source/'

def get_logo_path(): return IMG_FOLDER + "logoCelesc.png"
def get_report_code(): return "PBO-02-19 B"
def get_reg_code(): return "REG-302"
def get_pbo_code(): return "PBO-02"
def get_info_title(): return "INFORMAÇÕES SOBRE CONTINUIDADE"
def get_inspector(): return "RODRIGO"
def get_delta_t(): return "32,8"
def get_temp_ambient(): return "30"
def get_temp_object(): return "62,8"
def get_agency_region(): return "AGÊNCIA REGIONAL DE ITAJAÍ"
def get_feeder(): return "ALIMENTADOR"
def get_equipment(): return "EQUIPAMENTO"
def get_form_number(): return "NOTA Nº 810000068071"
def get_emissivity_val(): return "0.7"
def get_department_info(): return ("DIRETORIA DE DISTRIBUIÇÃO DEPARTAMENTO DE MANUTENÇÃO DO SISTEMA ELÉTRICO DIVISÃO DE MANUTENÇÃO DA DISTRIBUIÇÃO")
def get_dec_atual(): return "5.311"
def get_contrib_dec(): return "66.164"
def get_uc_conjunto(): return "9,00"
def get_uc_possiveis(): return "0,73"
def get_dec_date(): return "28/01/19"
def get_contrib_global(): return "0,007"
def get_situacao_dec(): return "BOM"
def get_location(): return "ITAPEMA, MORRETES, BR 101"
def get_description_long(): return ("TERMINAL SUPERIOR DA BY PASS LADO FONTE DA FASE DE DENTRO, TERMINAL INFERIOR DA BY PASS LADO FONTE DA FASE DE FORA, CONTATO SUPERIOR DA BY PASS LADO CARGA DA FASE DE FORA, TERMINAL E CONTATO SUPERIOR DA BY PASS LADO FONTE DA FASE DO MEIO")
def get_visual_image_path(): return IMG_FOLDER + "Img_Visual.jpg"
def get_thermal_image_path(): return IMG_FOLDER + "Img_Termica.jpg"
def get_timestamp(): return datetime.now()
def get_temp_max_equipment_value(): return "Isolador"
def get_model_path(): return 'best_V11_aug.pt'
def get_gps(): return GPS(-27.59, -48.54) # Florianópolis
def get_environmental_conditions(): return {'hr': 0.65, 'env_temp': 25}
def get_label_translation():
    return {
        "transformer" : "Transformador", "vertical-insulator" : "Isolador vertical",
        "horizontal-insulator" : "Isolador horizontal", "fuse-cutout" : "Chave fusivel",
        "overhead-switch" : "Chave faca", "connector" : "Conector", 'person': 'Pessoa' # YOLO model default
    }


def get_component_temperature_thresholds():
    """Returns a dict of danger temperature thresholds per component type."""
    return {
        # Raw label from model : Danger Temperature in Celsius
        "connector": 75,
        "fuse-cutout": 65,
        "overhead-switch": 70,
        "transformer": 90,
        "vertical-insulator": 40,
        "horizontal-insulator": 40,
        # Default for any component not explicitly listed above
        "default": 60
    }

def run():
    """
    Função principal (Controlador) que orquestra a coleta de dados,
    a execução da inferência e a geração do relatório.
    """
    output_pdf_path = "Final_Inspection_Report.pdf"
    
    # 1. Montar o dicionário de dados principal a partir das fontes de dados
    report_data = {
        'logo_path': get_logo_path(), 'report_code': get_report_code(),
        'reg_code': get_reg_code(), 'pbo_code': get_pbo_code(),
        'info_title': get_info_title(), 'inspector': get_inspector(),
        'delta_t': get_delta_t(), 'temp_ambient': get_temp_ambient(),
        'temp_object': get_temp_object(), 'agency_region': get_agency_region(),
        'feeder': get_feeder(), 'equipment': get_equipment(),
        'form_number': get_form_number(), 'emissivity_val': get_emissivity_val(),
        'department_info': get_department_info(), 'dec_atual': get_dec_atual(),
        'contrib_dec': get_contrib_dec(), 'uc_conjunto': get_uc_conjunto(),
        'uc_possiveis': get_uc_possiveis(), 'dec_date': get_dec_date(),
        'contrib_global': get_contrib_global(), 'situacao_dec': get_situacao_dec(),
        'location': get_location(), 'description_long': get_description_long(),
        'timestamp': get_timestamp(),
        'temp_max_equipment_value': get_temp_max_equipment_value(),
        'visual_image_path': get_visual_image_path(),
        'thermal_image_path': get_thermal_image_path(),
        'model_path': get_model_path(),
        'gps': get_gps(),
        'environmental_conditions': get_environmental_conditions(),
        'label_translation': get_label_translation(),
        'temp_thresholds': get_component_temperature_thresholds(),
    }

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # --- ETAPA DE INFERÊNCIA (delegada ao InferenceEngine) ---
            print("Step 1: Inicializando o motor de inferência...")
            engine = InferenceEngine(model_path=report_data['model_path'])
            
            # Executa a inferência para obter os resultados
            results = engine.run_inference(image_path=report_data['visual_image_path'])
            
            # Gera a imagem anotada usando o motor
            annotated_image_path = engine.generate_annotated_image(results, temp_dir)
            
            # (Opcional) Salvar resultados para depuração, como antes
            pickle_path = os.path.join(temp_dir, "inference_results.pkl")
            with open(pickle_path, 'wb') as f:
                pickle.dump({"resultado": results}, f)
            print(f"Resultados da inferência salvos em: {pickle_path}")

            # --- ETAPA DE GERAÇÃO DO RELATÓRIO ---
            # 2. Gerar a primeira parte do relatório (página de resumo)
            print("\nStep 2: Gerando a página de resumo...")
            report_generator = ReportGenerator(report_data)
            story = report_generator.generate_summary_story()
            print("Página de resumo criada.")

            # 3. Gerar e adicionar a segunda parte (análise detalhada)
            print("\nStep 3: Gerando a análise detalhada dos componentes...")
            analyzer = ComponentAnalyzer(report_data)
            analyzer.add_analysis_to_story(
                story,
                results=results,
                visual_img_path=report_data['visual_image_path'],
                thermal_img_path=report_data['thermal_image_path'],
                annotated_visual_image_path=annotated_image_path,
                temp_dir=temp_dir
            )
            print("Análise detalhada adicionada ao relatório.")

            # 4. Construir o PDF final a partir do 'story' combinado
            print("\nStep 4: Construindo o PDF final...")
            doc = SimpleDocTemplate(output_pdf_path, pagesize=A4)
            doc.build(story)
            print(f"Relatório criado com sucesso: {output_pdf_path}")

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run()