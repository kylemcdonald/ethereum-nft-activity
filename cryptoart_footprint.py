import json
import argparse
import datetime
from collections import defaultdict

from etherscan import Etherscan, sum_gas
from ethereum_footprint import EthereumFootprint
from nifty_gateway import list_nifty_gateway

parser = argparse.ArgumentParser(description='Estimate emissions footprint for CryptoArt platforms.')
parser.add_argument('--ng', action='store_true', help='Estimate footprint for Nifty Gateway.')
parser.add_argument('--summary', action='store_true', help='Summarize results by marketplace.')
parser.add_argument('--noupdate', action='store_false', help='Do not update cache.')
parser.add_argument('--commas', action='store_true', help='Print with comma separators.')
parser.add_argument('--startdate', default='', help='YYYY-MM-DD start date for transactions.')
parser.add_argument('--enddate', default='', help='YYYY-MM-DD end date for transactions.')
parser.add_argument('--verbose', action='store_true', help='Verbose mode.')
args = parser.parse_args()

start_date = None
end_date = None
if args.startdate != '':
    start_date = datetime.date.fromisoformat(args.startdate)
if args.enddate != '':
    end_date = datetime.date.fromisoformat(args.enddate)

with open('env.json') as f:
    apikey = json.load(f)['etherscan-api-key']
    
with open('data/contracts.json') as f:
    contracts = json.load(f)

etherscan = Etherscan(apikey)
ethereum_footprint = EthereumFootprint()

summary = defaultdict(lambda: defaultdict(int))
if not args.summary:
    print(f'Name\tKind\tAddress\tGas\tTransactions\tkgCO2')
for name_kind, address in contracts.items():
    if name_kind == 'Nifty Gateway/multiple':
        if args.ng:
            transactions = etherscan.load_transactions_multiple(list_nifty_gateway(args.verbose),
                update=args.noupdate,
                verbose=args.verbose)
        else:
            continue
    else:
        transactions = etherscan.load_transactions(address, update=args.noupdate, verbose=args.verbose)
    gas = sum_gas(transactions,
        start_date=start_date,
        end_date=end_date)
    kgco2 = int(ethereum_footprint.sum_kgco2(transactions,
        start_date=start_date,
        end_date=end_date))
    name, kind = name_kind.split('/')
    summary[name]['gas'] += gas 
    summary[name]['transactions'] += len(transactions)
    summary[name]['kgco2'] += kgco2
    if not args.summary:
        if args.commas:
            print(f'{name}\t{kind}\t{address}\t{gas:,}\t{len(transactions):,}\t{kgco2:,}')
        else:
            print(f'{name}\t{kind}\t{address}\t{gas}\t{len(transactions)}\t{kgco2}')

if args.summary:
    print('Name\tGas\tTransactions\tkgCO2')
    for name in sorted(summary.keys()):
        gas = summary[name]['gas']
        transactions = summary[name]['transactions']
        kgco2 = summary[name]['kgco2']
        print(f'{name}\t{gas:,}\t{transactions:,}\t{kgco2:,}')