from pynomo.nomographer import Nomographer

N_params_2 = {
    'u_min': 45,
    'u_max': 90,
    'function': lambda u: -0.0036*u,
    'title': r'$Age$',
    'tick_levels': 2,
    'tick_text_levels': 1,
}

N_params_1 = {
    'u_min': 16.0,
    'u_max': 31.0,
    'function': lambda u: -0.0114*u,
    'title': r'$BMI$',
    'tick_levels': 2,
    'tick_text_levels': 1,
    # 'scale_type': 'linear_smart',
}

N_params_3 = {
    'u_min': 3.3,
    'u_max': 3.65,
    'function': lambda u: u-2.9632,
    'title': r'$Pi10$',
    'tick_levels': 3,
    'tick_text_levels': 2,
}

block_1_params = {
    'block_type': 'type_1',
    'width': 16.0,
    'height': 8.0,
    'f1_params': N_params_1,
    'f2_params': N_params_2,
    'f3_params': N_params_3,
    'isopleth_values': [[17, 45, "x"], [30, 80, "x"]]
}

main_params = {
    'filename':
    'test_nomo.pdf',
    'paper_height':
    10.0,
    'paper_width':
    16.0,
    'block_params': [block_1_params],
    'tranformations': [('rotate', 0.01), ('scale paper')],
    'title_str':
    r'$Pi10=c + b1*Age + b2*Height$',
    'extra_texts': [{
        'x': 2.50,
        'y': 9.0,
        'text': 'Female Never Smoker',
        'width': 5,
    }]
}

Nomographer(main_params)
