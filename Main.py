import tempfile
import pickle
import os

from reportlab.platypus import SimpleDocTemplate, PageBreak, Image, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from ultralytics import YOLO

# --- Local Imports ---
from report_generator import ReportGenerator
from part_analysis import ComponentAnalyzer
from inference_engine import InferenceEngine
from get_utils import *



def run():
    """
    Função principal (Controlador) que orquestra a coleta de dados,
    o carregamento dos resultados da inferência e a geração do relatório.
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
        'pickle_path': get_pickle_path(),
        'gps': get_gps(),
        'environmental_conditions': get_environmental_conditions(),
        'label_translation': get_label_translation(),
        'diagnosis_function': get_diagnosis_by_component,
    }

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # --- ETAPA DE CARREGAMENTO DOS RESULTADOS (modificado) ---
            print("Step 1: Inicializando o motor e carregando resultados...")
            engine = InferenceEngine()
            
            # Carrega os resultados do arquivo pickle em vez de executar a inferência
            results = engine.load_inference_from_pickle(pickle_path=report_data['pickle_path'])
            
            # Gera a imagem anotada usando o motor
            annotated_image_path = engine.generate_annotated_image(results, temp_dir)

            # --- ETAPA DE GERAÇÃO DO RELATÓRIO ---
            # 2. Gerar a primeira parte do relatório (página de resumo)
            print("\nStep 2: Gerando a página de resumo...")
            report_generator = ReportGenerator(report_data)
            story = report_generator.generate_summary_story()
            print("Página de resumo criada.")
            story.append(PageBreak())

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