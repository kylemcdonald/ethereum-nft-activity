import requests
import json
import os
from itertools import count
from utils import valid_hash, prefix_contracts, generate_blocklist

def list_nifty_gateway(update=True, verbose=False):
    cache_fn = 'data/nifty-gateway-contracts.json'

    cache = {}
    if os.path.exists(cache_fn):
        if verbose:
            print('Loading Nifty Gateway contracts from cache...')
        with open(cache_fn) as f:
            cache = json.load(f)

    if not update:
        if verbose:
            print('Returning Nifty Gateway contracts from cache...')
        return cache

    cache = {v:k for k,v in cache.items()} # swap key/value

    blocklist = generate_blocklist()
    
    if verbose:
        print('Downloading from drops...')
    for current_page in count(1):
        url = f'https://api.niftygateway.com/drops/open/?size=100&current={current_page}'
        res = requests.get(url)
        results = json.loads(res.content)['listOfDrops']
        if len(results) == 0:
            break
        for drop in results:
            for item in drop['Exhibitions']:
                contract = item['contractAddress']
                url = item['storeURL']
                key = 'Nifty Gateway/' + url
                if contract in blocklist:
                    print('skipping', key, contract)
                    break
                cache[contract] = key
        if verbose:
            print('Page', current_page, 'total', len(cache))
    if verbose:
        print('Done.')

    if verbose:
        print(f'Filtered: total {len(cache)}')

    cache = {v:k for k,v in cache.items()} # swap key/value

    with open(cache_fn, 'w') as f:
        json.dump(cache, f, indent=2)

    return cache

if __name__ == '__main__':
    list_nifty_gateway(update=True, verbose=True)