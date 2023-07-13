import yaml
import re

from datetime import datetime, date
import os
from os.path import join


def processa_linha(line:str, layout:str, header_id = None) -> dict:
    first_character = line[0]
    registro = None

    if first_character == '0':
        registro = layout['retorno'].get('header_arquivo')
    elif first_character == '9':
        registro = layout['retorno'].get('trailer_arquivo')
    else:
         registro = layout['retorno'].get('detalhes').get(f'segmento_{first_character}')

    return processa_segmento(line, registro)

def processa_segmento(line: str, segmento: dict):
    return { key : get_value(line, **define_dataType(segmento[key])) for key in segmento}
        
def get_value(line, start, end, tp=str, format='%d/%m/%Y', precision=0, default=None):
    try:
        if tp == date:
            return datetime.strptime(line[start : end], '%d%m%y').strftime(format)
        elif tp == float:
            return int(line[start : end])/(10**precision)
        return tp(line[start : end].strip())
    except ValueError :
        return default

def define_dataType(segmento: dict) -> dict:
    dataType = {}
    dataType['start'] = segmento['pos'][0] -1
    dataType['end'] = segmento['pos'][1]
    dataType['default'] = segmento.get('default')
    dataType['tp'] = str

    if '9' in segmento['picture']:
        if 'V9' in segmento['picture']:
            dataType['tp'] = float
            dataType['precision'] = int(re.search(r'V9\((\d+)\)', segmento['picture']).group(1))
        else:
            dataType['tp'] = int
    elif 'D' in segmento['picture']:
        dataType['tp'] = date
    
    return dataType


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    base_path = os.getenv('BASE_PATH')
    layout_file = join(base_path,'bradesco_retorno.yaml')
    with open(layout_file) as y:
        layout = yaml.safe_load(y)
    with open(join(base_path,'CB090900.RET') )as f:
        lines = [processa_linha(line, layout) for line in f.readlines() if line]
        print(lines)
        