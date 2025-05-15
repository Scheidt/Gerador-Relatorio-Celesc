from report_Creator import *

sample_data = {
    # Logo da CELESC
    # Data e Hora
    'report_code':       "PBO-02-19 B",
    'report_date':       "02/19",
    'reg_code':          "REG-302",
    'pbo_code':          "PBO-02",
    'classification':    "CLASSIFICAÇÃO DA MANUTENÇÃO PROGRAMADA",
    'info_title':        "INFORMAÇÕES SOBRE CONTINUIDADE",
    'inspector':         "RODRIGO",
    'delta_t':           "32,8",
    'temp_ambient':      "30",
    'temp_object':       "62,8",
    'agency_region':     "AGÊNCIA REGIONAL DE ITAJAÍ",
    'feeder':            "", # Botar legenda
    'equipment':         "", # Botar legenda
    'form_number':       "NOTA Nº 810000068071",
    # Emulsividade
    'department_info':   (
        "DIRETORIA DE DISTRIBUIÇÃO DEPARTAMENTO DE MANUTENÇÃO DO SISTEMA "
        "ELÉTRICO DIVISÃO DE MANUTENÇÃO DA DISTRIBUIÇÃO"
    ),
    'dec_atual':         "5.311",
    'contrib_dec':       "66.164",
    'uc_conjunto':       "9,00",
    'uc_possiveis':      "0,73",
    'dec_date':          "28/01/19",
    'contrib_global':    "0,007",
    'situacao_dec':      "BOM",
    'location':          "ITAPEMA, MORRETES, BR 101",
    'data_value':        "0,290",
    'description_long':  (
        "TERMINAL SUPERIOR DA BY PASS LADO FONTE DA FASE DE DENTRO, "
        "TERMINAL INFERIOR DA BY PASS LADO FONTE DA FASE DE FORA, "
        "CONTATO SUPERIOR DA BY PASS LADO CARGA DA FASE DE FORA, "
        "TERMINAL E CONTATO SUPERIOR DA BY PASS LADO FONTE DA FASE DO MEIO"
    ),
    'visual_image_path':        "Img_Source/Img_Visual.jpg",
    'thermal_image_path':       "Img_Source/Img_Termica.jpg"
}

create_report_pdf(sample_data, "relatorio_exemplo.pdf")
