import glob
import json

known = {}
for fn in glob.glob('data/*contracts.json'):
    with open(fn) as f:
        contracts = json.load(f)
    for k,v in contracts.items():
        if v in known:
            known_k, known_fn = known[v]
            print(k, 'in', fn, 'is also', known_k, 'in', known_fn)
        known[v] = (k, fn)