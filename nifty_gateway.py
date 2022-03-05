import requests
import json
import os
from itertools import count
from utils import valid_hash, prefix_contracts, generate_blocklist

def list_nifty_gateway(update=True, verbose=False):
    cache_fn = 'data/nifty-gateway-contracts.json'

    cache = None
    known_contracts = []
    if os.path.exists(cache_fn):
        if verbose:
            print('Loading Nifty Gateway contracts from cache...')
        with open(cache_fn) as f:
            cache = json.load(f)
        known_contracts = list(cache.values())

    if not update and cache is not None:
        if verbose:
            print('Returning Nifty Gateway contracts from cache...')
        return cache

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

    combined = set(known_contracts + drop_contracts)
    if verbose:
        print(f'Combined: total {len(combined)}')

    blocklist = generate_blocklist()
    prefixed = prefix_contracts('Nifty Gateway', combined, blocklist)

    if verbose:
        print(f'Filtered: total {len(prefixed)}')

    with open(cache_fn, 'w') as f:
        json.dump(prefixed, f, indent=2)

    return prefixed

if __name__ == '__main__':
    list_nifty_gateway(update=True, verbose=True)