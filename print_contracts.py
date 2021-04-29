import json
from collections import defaultdict
from etherscan import Etherscan, etherscan_timestamp

with open('data/contracts.json') as f:
    contracts = json.load(f)

grouped = defaultdict(set)
for name_kind, address in contracts.items():
    name, kind = name_kind.split('/')
    grouped[name].update([(kind, address)])

etherscan = Etherscan()

for name, kinds_addresses in sorted(grouped.items()):
    print(f'### {name}\n')
    for kind, address in sorted(kinds_addresses):
        if kind == 'multiple':
            print('* Uses many separate contracts.')
        else:
            tx = etherscan.load_transactions(address)
            dates = [etherscan_timestamp(e) for e in tx]
            min_date = min(dates).date()
            max_date = max(dates).date()
            print(f'* [{kind}](https://etherscan.io/address/{address}) {min_date} to {max_date}')
    print()