import requests
import os
import json
import datetime
import time

from simplify_tx import simplify_tx

def etherscan_method_id(tx):
    return tx['input'][:10]

def etherscan_timestamp(tx):
    return datetime.datetime.fromtimestamp(int(tx['timeStamp']))

def etherscan_gas_fees(tx):
    return etherscan_gas_price(tx) * etherscan_gas_used(tx)

def etherscan_gas_price(tx):
    return int(tx['gasPrice'])

def etherscan_gas_used(tx):
    return int(tx['gasUsed'])

def filter_transactions(transactions, start_date=None, end_date=None):
    if start_date is None and end_date is None:
        return transactions
    filtered = []
    for tx in transactions:
        date = etherscan_timestamp(tx).date()
        if start_date is not None and date < start_date:
            continue
        if end_date is not None and date >= end_date:
            continue
        filtered.append(tx)
    return filtered

def sum_gas_used(transactions):
    return sum([etherscan_gas_used(tx) for tx in transactions])

def safe_dump(fn, obj):
    with open(fn, 'w') as f:
        try:
            json.dump(obj, f, separators=(',', ':'))
        except:
            # truncate files instead of writing corrupt json
            f.truncate()
            raise

class Etherscan():
    def __init__(self, apikey=None, cache_dir='cache'):
        self.apikey = apikey
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def load_abi(self, address, verbose=False):
        fn = os.path.join(self.cache_dir, address + '.abi.json')
        if os.path.exists(fn):
            with open(fn) as f:
                result = f.read()
        else:
            url = f'https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={self.apikey}'
            response = requests.get(url)
            result = response.json()['result']
            with open(fn, 'w') as f:
                f.write(result)
        if result == 'Contract source code not verified':
            return None
        return json.loads(result)

    def load_transactions(self, address, update=True, verbose=False, **kwargs):
        """
        Load transactions from cache if available, check Etherscan for updates, and
        save result to cache.
        """
        if self.apikey is None:
            update = False
        if verbose:
            print('load_transactions', address)
        fn = os.path.join(self.cache_dir, address + '.json')
        startblock = None
        transactions = []
        if os.path.exists(fn):
            with open(fn) as f:
                try:
                    transactions = json.load(f)
                except json.decoder.JSONDecodeError:
                    if verbose:
                        print('ignoring error while loading', fn)
                    pass
            if not update:
                return transactions
            if len(transactions):
                startblock = max([int(e['blockNumber']) for e in transactions])
                if verbose:
                    print('starting from cache at', startblock, 'with', len(transactions))
        # add new transactions
        new_transactions = self.fetch_transactions(address, startblock=startblock, verbose=verbose, **kwargs)
        # dedupe
        if len(new_transactions) > 0:
            transactions.extend(new_transactions)
            transactions = list({e['hash']:e for e in transactions}.values())
            safe_dump(fn, transactions)
        return transactions

    def fetch_transactions_in_range(self, address, startblock, endblock, ratelimit_sleep=1):
        url = f'https://api.etherscan.io/api?module=account&apikey={self.apikey}&action=txlist&address={address}'
        if startblock is not None:
            url += f'&startblock={startblock}'
        if endblock is not None:
            url += f'&endblock={endblock}'
        response = requests.get(url)
        try:
            result = response.json()['result']
            if 'rate limit' in result:
                print('hit rate limit, sleeping', ratelimit_sleep, 'seconds')
                ratelimit_sleep *= 2
                time.sleep(ratelimit_sleep)
                return self.fetch_transactions_in_range(address, startblock, endblock, ratelimit_sleep)
            return result
        except:
            print('error parsing transactions', url)
            return []

    def fetch_transactions(self, address, startblock=None, endblock=None, simplify=True, verbose=False):
        """
        To keep the entire inputData, set simplify=False.
        """
        all_transactions = []
        while True:
            transactions = self.fetch_transactions_in_range(address, startblock, endblock)
            try:
                if simplify:
                    transactions = list(map(simplify_tx, transactions))
            except TypeError:
                print('error', address, 'start block', startblock, 'end block', endblock, 'transactions', transactions)
            all_transactions.extend(transactions)
            if verbose:
                print('fetching block', startblock, 'total transactions', len(all_transactions))
            if len(transactions) < 1000:
                break
            # do not incremement the block, in case there are multiple transactions in one block
            # but spread across paginated results. we dedupe later.
            startblock = int(transactions[-1]['blockNumber'])
        return all_transactions

    def load_transactions_multiple(self, addresses, verbose=False, **kwargs):
        transactions = []
        for address in addresses:
            if verbose:
                print('load_transactions', address)
            for tx in self.load_transactions(address, **kwargs):
                transactions.append(tx)
        return transactions