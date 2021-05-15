import requests
import os
from collections import defaultdict
import pandas as pd
from io import StringIO
from nearest_dict import NearestDict
from utils import load_stats_endpoint

class EthereumStats:
    def __init__(self, update=False, verbose=False):
        self.cache_fn = 'data/ethereum_stats.csv'
        if update or not os.path.exists(self.cache_fn):
            self.update(verbose)

        df = pd.read_csv(self.cache_fn)
        dates = [e.date() for e in pd.to_datetime(df['Date'])]
        self.dates = dates

        def build_lookup(name, kind, scaling=1):
            values = [kind(e) * scaling for e in df[name]]
            return NearestDict(zip(dates, values))
        
        self.tx_count = build_lookup('tx', int)
        self.tx_fees = build_lookup('transactionfee', float, 1/1e18)
        self.block_count = build_lookup('blocks', int)
        self.block_rewards = build_lookup('blockreward', float)
        self.gas_used = build_lookup('gasused', int)
        self.price = build_lookup('etherprice', float)
        self.hashrate = build_lookup('hashrate', float)
        
        self.tx_count_total = sum(self.tx_count.values)
        self.tx_fees_total = sum(self.tx_fees.values)
        self.block_count_total = sum(self.block_count.values)
        self.block_rewards_total = sum(self.block_rewards.values)
        self.gas_used_total = sum(self.gas_used.values)
        self.price_total = sum(self.price.values)

    def update(self, verbose=False):
        collected = defaultdict(dict)

        def add_source(endpoint):
            headers = {'User-Agent': 'Chrome'}
            if verbose:
                print('Updating', endpoint)
            url = load_stats_endpoint(endpoint)
            res = requests.get(url, headers=headers)
            if verbose:
                print('\t', len(res.content), 'bytes')
            content = StringIO(res.content.decode('utf8'))
            rows = pd.read_csv(content)
            for date, _, value in rows.values:
                collected[date][endpoint] = value

        add_source('tx')
        add_source('transactionfee')
        add_source('blocks')
        add_source('blockreward')
        add_source('gasused')
        add_source('etherprice')
        add_source('hashrate')

        df = pd.DataFrame(collected).transpose()
        df.index.name = 'Date'
        df.to_csv(self.cache_fn)

if __name__ == '__main__':
    EthereumStats(verbose=True, update=True)