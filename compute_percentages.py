import pandas as pd
from collections import defaultdict
from ethereum_stats import EthereumStats
from utils import get_timestamp

stats = EthereumStats()

compiled = defaultdict(dict)
for kind, name, baseline in [('tx-count', 'Transactions', stats.tx_count),
                       ('gas', 'Gas', stats.gas_used),
                       ('fees', 'Fees', stats.tx_fees)]:
    data = pd.read_csv(f'output/2021-05-04-23-06-22-{kind}.csv', index_col='Date')
    totals = data.values.sum(1)
    dates = [e.date() for e in pd.to_datetime(data.index)]
    for date, value in zip(dates, totals):
        compiled[date][name] = value / baseline[date]

df = pd.DataFrame(compiled).transpose()
df.index.name = 'Date'
today = get_timestamp()
df.to_csv(f'output/{today}-percentages.csv')