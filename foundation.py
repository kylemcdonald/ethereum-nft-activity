import json
from etherscan import Etherscan
from utils import load_etherscan_api_key
from utils import valid_hash, prefix_contracts

api_key = load_etherscan_api_key()
etherscan = Etherscan(api_key, read_only=True)

deployer = '0x3b612a5b49e025a6e4ba4ee4fb1ef46d13588059'
transactions = etherscan.fetch_transactions_internal(deployer, verbose=True)
contracts = [e['contractAddress'] for e in transactions]
prefixed = prefix_contracts('Foundation', contracts, blocklist=[deployer])

with open('data/foundation-contracts.json', 'w') as f:
    json.dump(prefixed, f, indent=2)