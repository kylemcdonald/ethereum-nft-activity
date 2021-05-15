import requests
import json
import os
from itertools import count

blocklist = [
    '0x06012c8cf97bead5deae237070f9587f8e7a266d' # cryptokitties
]

def valid_hash(hash):
    if hash in blocklist:
        return False
    return hash.startswith('0x') and len(hash) == 42
    
def list_nifty_gateway(update=True, verbose=False):
    cache_fn = 'data/nifty-gateway-contracts.json'

    if not update and os.path.exists(cache_fn):
        if verbose:
            print('Loading Nifty Gateway contracts from cache...')
        with open(cache_fn) as f:
            return json.load(f)

    drop_contracts = []
    if verbose:
        print('Downloading from drops...')
    for current_page in count(1):
        url = f'https://api.niftygateway.com/drops/open/?size=100&current={current_page}'
        res = requests.get(url)
        results = json.loads(res.content)['listOfDrops']
        if len(results) == 0:
            break
        contracts = [item['contractAddress'] for drop in results for item in drop['Exhibitions']]
        drop_contracts.extend(contracts)
        if verbose:
            print('Page', current_page, 'total', len(drop_contracts))
    if verbose:
        print('Done.')

    exhibition_contracts = []
    if verbose:
        print('Downloading from exhibition...')
    url = f'https://api.niftygateway.com/exhibition/open/'
    res = requests.get(url)
    results = json.loads(res.content)
    contracts = [e['contractAddress'] for e in results]
    exhibition_contracts.extend(contracts)
    if verbose:
        print('Done.')

    filtered = {}
    combined = set(exhibition_contracts + drop_contracts)
    for i, hash in enumerate(combined):
        if not valid_hash(hash):
            continue
        filtered[f'Nifty Gateway/{i}'] = hash

    with open(cache_fn, 'w') as f:
        json.dump(filtered, f, indent=2)

    return filtered

if __name__ == '__main__':
    list_nifty_gateway(update=True, verbose=True)