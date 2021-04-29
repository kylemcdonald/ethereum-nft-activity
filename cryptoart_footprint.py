import json
import argparse
import datetime
from collections import defaultdict

from etherscan import Etherscan, filter_transactions, sum_gas_used
from ethereum_footprint import EthereumFootprint
from nifty_gateway import list_nifty_gateway
from utils import load_contracts, load_etherscan_api_key, write_results_tsv, write_results_json

parser = argparse.ArgumentParser(description='Estimate emissions footprint for CryptoArt platforms.')
parser.add_argument('--ng', action='store_true', help='Estimate footprint for Nifty Gateway.')
parser.add_argument('--summary', action='store_true', help='Summarize results by marketplace.')
parser.add_argument('--noupdate', action='store_false', help='Do not update cache.')
parser.add_argument('--startdate', default='', help='YYYY-MM-DD start date for transactions.')
parser.add_argument('--enddate', default='', help='YYYY-MM-DD end date for transactions.')
parser.add_argument('--tsv', action='store_true', help='Output to TSV instead of JSON')
parser.add_argument('--verbose', action='store_true', help='Verbose mode.')
args = parser.parse_args()

start_date = None
end_date = None
if args.startdate != '':
    start_date = datetime.date.fromisoformat(args.startdate)
if args.enddate != '':
    end_date = datetime.date.fromisoformat(args.enddate)

api_key = load_etherscan_api_key()
contracts = load_contracts()
etherscan = Etherscan(api_key)
ethereum_footprint = EthereumFootprint()

summary = defaultdict(lambda: defaultdict(int))

output_json = {}
output_json['data'] = []

for name_kind, address in contracts.items():
    if name_kind.startswith('Nifty Gateway'):
        if not args.ng:
            continue # skip nifty gateway if user doesn't ask for it

    if name_kind == 'Nifty Gateway/multiple':
        addresses = list_nifty_gateway(
            update=args.noupdate,
            verbose=args.verbose)
        transactions = etherscan.load_transactions_multiple(addresses,
            update=args.noupdate,
            verbose=args.verbose)
    else:
        transactions = etherscan.load_transactions(address,
            update=args.noupdate,
            verbose=args.verbose)

    transactions = filter_transactions(transactions, start_date, end_date)
    gas = sum_gas_used(transactions)
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

if args.tsv:
    write_results_tsv(output_json)
else:
    write_results_json(output_json)