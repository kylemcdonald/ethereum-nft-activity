import json
import datetime

def load_etherscan_api_key():
    with open('env.json') as file:
        payload = json.load(file)
    return payload['etherscan-api-key']

def load_contracts(fn):
    if fn is None:
        fn = 'data/contracts.json'
    with open(fn) as file:
        return json.load(file)

def write_results_json(output):
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    result_filepath = f'output/{current_datetime}.json'
    with open(result_filepath, 'w') as f:
        json.dump(output, f)
    print(f'Emissions results saved to file: "{result_filepath}"')

def write_results_tsv(output):
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
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