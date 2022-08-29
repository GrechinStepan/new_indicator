import re
import json
import requests

from bs4 import BeautifulSoup


url = 'https://www.fedstat.ru/indicator/31074'
need = {'57937': 1707674, '58273': 1748984}


def save_file(url):
    response = requests.post(f'{url}?format=excel', data=get_payload())
    with open('real_test.xls', 'wb') as f:
        f.write(response.content)


def get_html(url):
    response = requests.get(url)

    return response.content


def html_parse():
    soup = BeautifulSoup(get_html(url), 'lxml')
    script = soup.find(
        'script', text=re.compile('filters')
    ).text.replace(' ', '')

    return script


def get_json(script):
    start_phrase = "window['grid']=newFGrid("
    start = script.find(start_phrase)
    end = script.find(');')

    return script[start + len(start_phrase): end]


def convert_json():
    row = get_json(html_parse()).replace("block:$('#grid'),", "")
    row = re.sub(r'([\{\s,])(\w+)(:)', r'\1"\2"\3', row)
    row = re.sub(r"'\S*'", '""', row)

    return json.loads(row)


def get_filters():
    json_str = convert_json()
    list_of_filters = list(json_str['filters'].keys())
    fil = {}
    for lof in list_of_filters:
        filters = []
        values_by_filter = json_str['filters'][lof]['values'].keys()
        filters.extend([f'{lof}_{param}' for param in values_by_filter])
        fil[lof] = filters

    return fil


def change_filters(need):
    all_filters = get_filters()
    for k, v in need.items():
        all_filters[k] = [f'{k}_{v}']

    return all_filters


def get_payload():
    json_str = convert_json()
    selcted_filters = [
        item for sublist in change_filters(need).values() for item in sublist
    ]
    payload = {
        'id': json_str['id'],
        'lineObjectIds': json_str['left_columns'],
        'columnObjectIds': json_str['top_columns'],
        'filterObjectIds': [*json_str['filterObjectIds'], 0],
        'selectedFilterIds': selcted_filters
    }

    return payload


save_file(url)
