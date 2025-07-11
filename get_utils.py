# get_utils.py
from datetime import datetime
from reportlab.lib import colors

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
def get_pickle_path(): return 'pickle_resultado_inferencia.pkl'
def get_gps(): return GPS(-27.59, -48.54) # Florianópolis
def get_environmental_conditions(): return {'hr': 0.65, 'env_temp': 25}
def get_label_translation():
    return {
        "transformer" : "Transformador", "vertical-insulator" : "Isolador vertical",
        "horizontal-insulator" : "Isolador horizontal", "fuse-cutout" : "Chave fusivel",
        "overhead-switch" : "Chave faca", "connector" : "Conector", 'person': 'Pessoa'
    }

def get_diagnosis_by_component(component_label, delta_t):
    """
    Determina o diagnóstico e a cor com base no tipo de componente e no delta_t.
    Retorna uma tupla (texto_do_diagnostico, cor_reportlab).
    """
    # Thresholds de Delta T em Celsius para cada diagnóstico: (Programada, Imediata, Urgente)
    thresholds = {
        "connector":              (20, 40, 60),
        "fuse-cutout":            (15, 30, 50),
        "overhead-switch":        (15, 35, 55),
        "transformer":            (25, 50, 75),
        "vertical-insulator":     (10, 20, 40),
        "horizontal-insulator":   (10, 20, 40),
        "default":                (10, 30, 60)
    }
    
    prog_thresh, imed_thresh, urg_thresh = thresholds.get(component_label, thresholds["default"])

    if delta_t >= urg_thresh:
        return "Manutenção Urgente", colors.Color(0.8, 0, 0)
    elif delta_t >= imed_thresh:
        return "Manutenção Imediata", colors.red
    elif delta_t >= prog_thresh:
        return "Manutenção Programada", colors.orange
    else:
        return "Sem Manutenção", colors.lightgreen