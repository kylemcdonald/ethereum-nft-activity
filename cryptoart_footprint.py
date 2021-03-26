import json
import argparse
from collections import defaultdict

from etherscan import Etherscan, sum_gas
from ethereum_footprint import EthereumFootprint
from nifty_gateway import list_nifty_gateway
from utils import load_contracts, load_etherscan_api_key, write_results

parser = argparse.ArgumentParser(description='Estimate emissions footprint for CryptoArt platforms.')
parser.add_argument('--ng', action='store_true', help='Estimate footprint for Nifty Gateway.')
parser.add_argument('--summary', action='store_true', help='Summarize results by marketplace.')
parser.add_argument('--commas', action='store_true', help='Print with comma separators.')
parser.add_argument('--verbose', action='store_true', help='Verbose mode.')
args = parser.parse_args()

api_key = load_etherscan_api_key()
contracts = load_contracts()

etherscan = Etherscan(api_key)
ethereum_footprint = EthereumFootprint()

summary = defaultdict(lambda: defaultdict(int))

output_json = {}
output_json['data'] = []

def load_transactions():
    if name_kind == 'Nifty Gateway/multiple':
        transactions = etherscan.load_transactions_multiple(list_nifty_gateway(args.verbose), verbose=args.verbose)
    else:
        transactions = etherscan.load_transactions(address, verbose=args.verbose)
    return transactions

for name_kind, address in contracts.items():
    # Skip Nifty Gateway if user doesn't ask for it
    if name_kind == 'Nifty Gateway/multiple' and not args.ng:
        continue

    transactions = load_transactions()
    gas = sum_gas(transactions)
    kgco2 = int(ethereum_footprint.sum_kgco2(transactions))
    name, kind = name_kind.split('/')
    summary[name]['gas'] += gas
    summary[name]['transactions'] += len(transactions)
    summary[name]['kgco2'] += kgco2

    if not args.summary:
        row = {
            'name': name,
            'kind': kind,
            'address': address,
            'gas': gas,
            'transactions': len(transactions),
            'kgco2': kgco2
        }
        output_json['data'].append(row)

if args.summary:
    for name in sorted(summary.keys()):
        gas = summary[name]['gas']
        transactions = summary[name]['transactions']
        kgco2 = summary[name]['kgco2']
        row = {
            'name': name,
            'gas': gas,
            'transactions': transactions,
            'kgco2': kgco2
        }
        output_json['data'].append(row)

write_results(output_json)