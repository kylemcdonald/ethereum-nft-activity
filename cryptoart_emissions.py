import json
import argparse

from etherscan import Etherscan, sum_gas
from ethereum_emissions import EthereumEmissions
from nifty_gateway import list_nifty_gateway

parser = argparse.ArgumentParser(description='Estimate emissions for CryptoArt platforms.')
parser.add_argument('--ng', action='store_true', help='Estimate emissions for Nifty Gateway.')
parser.add_argument('--verbose', action='store_true', help='Verbose mode.')
args = parser.parse_args()

with open('env.json') as f:
    apikey = json.load(f)['etherscan-api-key']
    
with open('data/contracts.json') as f:
    contracts = json.load(f)

etherscan = Etherscan(apikey)
ethereum_emissions = EthereumEmissions()

print(f'Name\tKind\tAddress\tGas\tTransactions\tkgCO2')
for name_kind, address in contracts.items():
    if name_kind == 'Nifty Gateway/multiple':
        if args.ng:
            transactions = etherscan.load_transactions_multiple(list_nifty_gateway(args.verbose),
                verbose=args.verbose)
        else:
            continue
    else:
        transactions = etherscan.load_transactions(address, verbose=args.verbose)
    gas = sum_gas(transactions)
    kgco2 = int(ethereum_emissions.sum_kgco2(transactions))
    name, kind = name_kind.split('/')
    print(f'{name}\t{kind}\t{address}\t{gas}\t{len(transactions)}\t{kgco2}')