from report_Creator import *
from datetime import datetime
from image_masker import mask_image

IMG_FOLDER = 'img_Source/'

def get_logo_path():
    return IMG_FOLDER + "logoCelesc.png"

def get_report_code():
    return "PBO-02-19 B"

def get_report_date():
    return datetime.now().strftime("%d/%m")

def get_reg_code():
    return "REG-302"

def get_pbo_code():
    return "PBO-02"

def get_classification():
    return "CLASSIFICAÇÃO DA MANUTENÇÃO PROGRAMADA"

def get_info_title():
    return "INFORMAÇÕES SOBRE CONTINUIDADE"

def get_inspector():
    return "RODRIGO"

def get_delta_t():
    return "32,8"

def get_temp_ambient():
    return "30"

def get_temp_object():
    return "62,8"

def get_operation():
    return "RECOMENDAÇÃO"

def get_agency_region():
    return "AGÊNCIA REGIONAL DE ITAJAÍ"

def get_feeder():
    return "ALIMENTADOR"

def get_equipment():
    return "EQUIPAMENTO"

def get_form_number():
    return "NOTA Nº 810000068071"

def get_emissivity():
    return "EMISSIVIDADE"

def get_department_info():
    return (
        "DIRETORIA DE DISTRIBUIÇÃO DEPARTAMENTO DE MANUTENÇÃO DO SISTEMA "
        "ELÉTRICO DIVISÃO DE MANUTENÇÃO DA DISTRIBUIÇÃO"
    )

def get_dec_atual():
    return "5.311"

def get_contrib_dec():
    return "66.164"

def get_uc_conjunto():
    return "9,00"

def get_uc_possiveis():
    return "0,73"

def get_dec_date():
    return "28/01/19"

def get_contrib_global():
    return "0,007"

def get_situacao_dec():
    return "BOM"

def get_location():
    return "ITAPEMA, MORRETES, BR 101"

def get_data_value():
    return "0,290"

def get_description_long():
    return (
        "TERMINAL SUPERIOR DA BY PASS LADO FONTE DA FASE DE DENTRO, "
        "TERMINAL INFERIOR DA BY PASS LADO FONTE DA FASE DE FORA, "
        "CONTATO SUPERIOR DA BY PASS LADO CARGA DA FASE DE FORA, "
        "TERMINAL E CONTATO SUPERIOR DA BY PASS LADO FONTE DA FASE DO MEIO"
    )

def get_visual_image_path():
    return IMG_FOLDER + "Img_Visual.jpg"

def get_thermal_image_path():
    return IMG_FOLDER + "Img_Termica.jpg"

def get_timestamp():
    return datetime.now()

def get_temp_max_equipment_value():
    return "Isolador" # Or fetch from actual source

def get_masked_image_path():
    return mask_image(IMG_FOLDER)

def get_model_path():
    return 'best_V11_aug.pt'

# Populate the dictionary by calling the getter functions
sample_data = {
    'logo_path': get_logo_path(),
    'report_code': get_report_code(),
    'report_date': get_report_date(),
    'reg_code': get_reg_code(),
    'pbo_code': get_pbo_code(),
    'classification': get_classification(),
    'info_title': get_info_title(),
    'inspector': get_inspector(),
    'temp_ambient': get_temp_ambient(),
    'temp_object': get_temp_object(),
    'delta_t': get_delta_t(),
    'operation': get_operation(),
    'agency_region': get_agency_region(),
    'feeder': get_feeder(),
    'equipment': get_equipment(),
    'form_number': get_form_number(),
    'emissivity': get_emissivity(),
    'department_info': get_department_info(),
    'dec_atual': get_dec_atual(),
    'contrib_dec': get_contrib_dec(),
    'uc_conjunto': get_uc_conjunto(),
    'uc_possiveis': get_uc_possiveis(),
    'dec_date': get_dec_date(),
    'contrib_global': get_contrib_global(),
    'situacao_dec': get_situacao_dec(),
    'location': get_location(),
    'data_value': get_data_value(),
    'timestamp': get_timestamp(),
    'description_long': get_description_long(),
    'visual_image_path': get_visual_image_path(),
    'thermal_image_path': get_thermal_image_path(),
    'temp_max_equipment_value': get_temp_max_equipment_value(),
    'masked_image_path': get_masked_image_path(),
    'model_path': get_model_path(),
}



create_report_pdf(sample_data, "relatorio_exemplo.pdf")
