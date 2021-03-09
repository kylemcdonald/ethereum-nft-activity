import requests
import os
import json
import datetime
import os

blocklist = [
    '0x06012c8cf97bead5deae237070f9587f8e7a266d' # cryptokitties
]

def etherscan_timestamp(tx):
    return datetime.datetime.fromtimestamp(int(tx['timeStamp']))

def etherscan_gas(tx):
    return int(tx['gasUsed'])

def sum_gas(transactions, start_date=None, end_date=None):
    gas = 0
    for tx in transactions:
        if start_date is not None or end_date is not None:
            date = etherscan_timestamp(tx).date()
            if start_date is not None and date < start_date:
                continue
            if end_date is not None and date >= end_date:
                continue
        gas += etherscan_gas(tx)
    return gas

class Etherscan():
    def __init__(self, apikey, cache_dir='cache'):
        self.apikey = apikey
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def load_transactions(self, address, update=True, verbose=False, **kwargs):
        """
        Load transactions from cache if available, check Etherscan for updates, and
        save result to cache.
        """
        if address in blocklist:
            return []
        if verbose:
            print(address)
        fn = os.path.join(self.cache_dir, address + '.json')
        startblock = None
        transactions = []
        if os.path.exists(fn):
            with open(fn) as f:
                transactions = json.load(f)
            if not update:
                return transactions
            startblock = max([int(e['blockNumber']) for e in transactions])
            if verbose:
                print('starting at', startblock, 'with', len(transactions))
        # add new transactions
        transactions.extend(self.fetch_transactions(address, startblock=startblock, verbose=verbose, **kwargs))
        # dedupe
        transactions = list({e['hash']:e for e in transactions}.values())
        with open(fn, 'w') as f:
            json.dump(transactions, f)
        return transactions

    def fetch_transactions_in_range(self, address, startblock, endblock):
        url = f'https://api.etherscan.io/api?module=account&apikey={self.apikey}&action=txlist&address={address}'
        if startblock is not None:
            url += f'&startblock={startblock}'
        if endblock is not None:
            url += f'&endblock={endblock}'
        response = requests.get(url)
        return response.json()['result']

    def fetch_transactions(self, address, startblock=None, endblock=None, simplify=True, verbose=False):
        """
        To keep all the data from Etherscan, set simplify=False.
        """
        all_transactions = []
        while True:
            transactions = self.fetch_transactions_in_range(address, startblock, endblock)
            try:
                if simplify:
                    transactions = [{
                        'hash': e['hash'],
                        'blockNumber': e['blockNumber'],
                        'gasUsed': e['gasUsed'],
                        'timeStamp': e['timeStamp']
                    } for e in transactions]
            except TypeError:
                print(address, startblock, endblock, transactions)
            all_transactions.extend(transactions)
            if verbose:
                print(startblock, len(all_transactions))
            if len(transactions) < 10000:
                break
            # do not incremement the block, in case there are multiple transactions in one block
            # but spread across paginated results. we dedupe later.
            startblock = int(transactions[-1]['blockNumber'])
        return all_transactions

    def load_transactions_multiple(self, addresses, verbose=False, **kwargs):
        transactions = []
        for address in addresses:
            if verbose:
                print(address)
            for tx in self.load_transactions(address, **kwargs):
                transactions.append(tx)
        return transactions