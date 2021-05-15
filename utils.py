import json
import datetime
import csv
from io import StringIO

def read_csv(fn, skip_header=True):
    with open(fn) as f:
        reader = csv.reader(f)
        if skip_header:
            next(reader)
        for row in reader:
            yield row

def read_csv_string(text, skip_header=True):
    if type(text) == bytes:
        text = text.decode('utf8')
    f = StringIO(text)
    reader = csv.reader(f)
    if skip_header:
        next(reader)
    for row in reader:
        yield row

def load_etherscan_api_key():
    with open('env.json') as file:
        payload = json.load(file)
    return payload['etherscan-api-key']

def load_stats_endpoint(endpoint):
    url = 'https://etherscan.io/chart/{}?output=csv'
    with open('env.json') as f:
        env = json.load(f)
    if 'stats-endpoint' in env:
        url = env['stats-endpoint']
    return url.format(endpoint)

def load_contracts(fns=None):
    if fns is None:
        fns = ['data/contracts.json']
    contracts = {}
    for fn in fns:
        with open(fn) as file:
            contracts.update(json.load(file))
    return contracts

def get_timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

def write_results_json(output):
    current_datetime = get_timestamp()
    result_filepath = f'output/{current_datetime}.json'
    with open(result_filepath, 'w') as f:
        json.dump(output, f)
    print(f'Emissions results saved to file: "{result_filepath}"')

def write_results_tsv(output):
    current_datetime = get_timestamp()
    result_filepath = f'output/{current_datetime}.tsv'
    cols = list(output['data'][0].keys())
    with open(result_filepath, 'w') as f:
        f.write('\t'.join(cols) + '\n')
        for e in output['data']:
            values = [str(e[key]) for key in cols]
            f.write('\t'.join(values) + '\n')
    print(f'Emissions results saved to file: "{result_filepath}"')

def split_name_kind(name_kind):
    parts = name_kind.split('/')
    name = '/'.join(parts[:-1])
    kind = parts[-1]
    return name, kind