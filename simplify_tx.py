import os
import json
from tqdm import tqdm

to_remove = [
    'nonce',
    'blockHash',
    'transactionIndex',
    'from',
    'to',
    'value',
    'isError',
    'txreceipt_status',
    'contractAddress',
    'cumulativeGasUsed',
    'gas',
    'confirmations'
]

def simplify_tx(tx):
    if 'input' in tx:
        tx['input'] = tx['input'][:10]
    for key in to_remove:
        if key in tx:
            del tx[key]
    return tx

if __name__ == '__main__':
    in_root = 'cache'
    out_root = 'cache-simple'
    fns = os.listdir(in_root)
    for fn in tqdm(fns):
        if fn.endswith('.abi.json'):
            continue
        try:
            in_fn = os.path.join(in_root, fn)
            out_fn = os.path.join(out_root, fn)
            if os.path.exists(out_fn):
                continue
            with open(in_fn) as f:
                data = json.load(f)
            filtered = list(map(simplify_tx, data))
            with open(out_fn, 'w') as f:
                json.dump(filtered, f, separators=(',', ':'))
        except json.decoder.JSONDecodeError:
            print('error', in_fn)
            raise