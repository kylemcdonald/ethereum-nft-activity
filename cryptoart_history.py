import json
import argparse
import datetime
from collections import defaultdict
import pandas as pd

from etherscan import Etherscan, etherscan_timestamp, etherscan_gas_fees, etherscan_gas_used
from nifty_gateway import list_nifty_gateway
from utils import load_contracts, load_etherscan_api_key, split_name_kind

parser = argparse.ArgumentParser(description='Calculate total gas used and transaction fees paid by CryptoArt platforms.')
parser.add_argument('--ng', action='store_true', help='Include Nifty Gateway.')
parser.add_argument('--contracts', default=None, help='Use a specific list of contracts.')
parser.add_argument('--noupdate', action='store_false', help='Do not update cache.')
parser.add_argument('--verbose', action='store_true', help='Verbose mode.')
args = parser.parse_args()

api_key = load_etherscan_api_key()
contracts = load_contracts(args.contracts)
etherscan = Etherscan(api_key)

gas_data = defaultdict(lambda:defaultdict(int))
fee_data = defaultdict(lambda:defaultdict(int))

for name_kind, address in contracts.items():

    if args.verbose:
        print(name_kind)

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
    
    if args.verbose:
        print(f'\ttransactions {len(transactions)}')
        print(f'\tgas_used {all_gas_used:,}')
        print(f'\tgas_fees {all_gas_fees/1e18:.2f} ETH')

today = datetime.datetime.now().date().isoformat()

fn = f'output/{today}-fees.csv'
if args.verbose:
    print(f'Writing fees to {fn}')

df = pd.DataFrame(fee_data) / 1e18 # convert from wei to ether
df.index.name = 'Totals for data'
df = df.sort_values('Totals for data', ascending=False)
df = df.fillna(0)
df.to_csv(fn)

fn = f'output/{today}-gas.csv'
if args.verbose:
    print(f'Writing gas to {fn}')

df = pd.DataFrame(gas_data)
df.index.name = 'Totals for data'
df = df.sort_values('Totals for data', ascending=False)
df = df.fillna(0)
df = df.astype(int)
df.to_csv(fn)