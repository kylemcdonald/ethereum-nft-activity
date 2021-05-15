import json
import argparse
import datetime
from collections import defaultdict
import pandas as pd

from etherscan import Etherscan, etherscan_timestamp, etherscan_gas_fees, etherscan_gas_used
from utils import load_contracts, load_etherscan_api_key, split_name_kind, get_timestamp

parser = argparse.ArgumentParser(description='Calculate total gas used and transaction fees paid by Ethereum platforms.')
parser.add_argument('contracts', nargs='+', help='List of contract JSON filenames')
parser.add_argument('--prefix', type=str, default=get_timestamp(), help='Output file prefix. Default: date and time.')
parser.add_argument('--noupdate', action='store_false', help='Do not update cache.')
parser.add_argument('--simplify', action='store_true', help='Simplify transactions to minimize cache size.')
parser.add_argument('--verbose', action='store_true', help='Verbose mode.')
args = parser.parse_args()

api_key = load_etherscan_api_key()
contracts = load_contracts(args.contracts)
etherscan = Etherscan(api_key)

gas_data = defaultdict(lambda:defaultdict(int))
fee_data = defaultdict(lambda:defaultdict(int))
tx_count_data = defaultdict(lambda:defaultdict(int))

for name_kind, address in contracts.items():

    if args.verbose:
        print(name_kind)

    transactions = etherscan.load_transactions(address,
        update=args.noupdate,
        simplify=args.simplify,
        verbose=args.verbose)
        
    name, kind = split_name_kind(name_kind)

    all_gas_fees = 0
    all_gas_used = 0
    for tx in transactions:
        date = etherscan_timestamp(tx).date()
        gas_used = etherscan_gas_used(tx)
        gas_data[name][date] += gas_used
        all_gas_used += gas_used
        gas_fees = etherscan_gas_fees(tx)
        fee_data[name][date] += gas_fees
        all_gas_fees += gas_fees
        tx_count_data[name][date] += 1
    
    if args.verbose:
        print(f'\ttransactions {len(transactions)}')
        print(f'\tgas_used {all_gas_used:,}')
        print(f'\tgas_fees {all_gas_fees/1e18:.2f} ETH')

def save_csv(data, fn, kind, scaling=None):
    if args.verbose:
        print(f'Writing to {fn}')
    df = pd.DataFrame(data)
    df.index.name = 'Date'
    df = df.sort_values('Date', ascending=True)
    df = df.fillna(0)
    if scaling is not None:
        df *= scaling
    df = df.astype(kind)
    df.to_csv(fn)

prefix = args.prefix
save_csv(fee_data, f'output/{prefix}-fees.csv', float, 1/1e18)
save_csv(gas_data, f'output/{prefix}-gas.csv', int)
save_csv(tx_count_data, f'output/{prefix}-tx-count.csv', int)