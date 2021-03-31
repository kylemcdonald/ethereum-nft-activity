import json
from collections import defaultdict 

with open('data/contracts.json') as f:
    contracts = json.load(f)

grouped = defaultdict(set)
for name_kind, address in contracts.items():
    name, kind = name_kind.split('/')
    grouped[name].update([(kind, address)])

for name, kinds_addresses in sorted(grouped.items()):
    print(f'### {name}\n')
    for kind, address in sorted(kinds_addresses):
        if kind == 'multiple':
            print('Uses many separate contracts.')
        else:
            print(f'* [{kind}](https://etherscan.io/address/{address})')
    print()