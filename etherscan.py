import requests
import datetime
import sqlite3
import time

def filter_transactions(transactions, start_date=None, end_date=None):
    if start_date is None and end_date is None:
        return transactions
    filtered = []
    for tx in transactions:
        date = tx.get_datetime()
        if start_date is not None and date < start_date:
            continue
        if end_date is not None and date >= end_date:
            continue
        filtered.append(tx)
    return filtered

class Transaction:
    def __init__(self, tx_hash, block_number, timestamp, gas_price, gas_used):
        self.tx_hash = tx_hash
        self.block_number = block_number
        self.timestamp = timestamp
        self.gas_price = gas_price
        self.gas_used = gas_used

    def __repr__(self):
        return '0x' + self.tx_hash.hex()

    def get_fees(self):
        return self.gas_price * self.gas_used

    def get_datetime(self):
        return datetime.datetime.fromtimestamp(self.timestamp)

def sum_gas_used(transactions):
    return sum([tx.gas_used for tx in transactions])

def hash0x_to_bytes(hash0x):
    return bytearray.fromhex(hash0x[2:])

def build_rows(transactions):
    for tx in transactions:
        yield (
            hash0x_to_bytes(tx['hash']),
            int(tx['blockNumber']),
            int(tx['timeStamp']),
            int(tx['gasPrice']),
            int(tx['gasUsed']))

class Etherscan():
    def __init__(self, apikey=None, db_file='transactions.sqlite3', read_only=False):
        self.apikey = apikey
        self.db_file = db_file
        flags = '?mode=ro' if read_only else ''
        self.db = sqlite3.connect(f'file:{db_file}{flags}', uri=True)
    
    def execute(self, cmd):
        return self.db.cursor().execute(cmd)
    
    def insert_transactions(self, address, transactions):
        cmd = f'insert or replace into "{address.lower()}" values (?, ?, ?, ?, ?)'
        self.db.cursor().executemany(cmd, build_rows(transactions))
        
    def create_transactions_table(self, address):
        return self.execute(
            f'create table if not exists "{address.lower()}" (\
            hash blob primary key, \
            block_number integer key, \
            timestamp integer, \
            gas_price integer, \
            gas_used integer)')
    
    def list_transactions(self, address):
        for row in self.execute(f'select * from "{address.lower()}"'):
            yield Transaction(*row)

    def count_transactions(self, address):
        return self.execute(f'select count(*) from "{address.lower()}"').fetchone()[0]
    
    def latest_block(self, address):
        return self.execute(f'select max(block_number) from "{address.lower()}"').fetchone()[0]

    def load_transactions(self, address, update=True, verbose=False, **kwargs):
        if self.apikey is None:
            update = False
        if verbose:
            print('load_transactions', address)
        self.create_transactions_table(address)        
        if not update:
            return self.list_transactions(address)
        self.fetch_transactions(address, verbose=verbose, **kwargs)
        self.db.commit()
        return self.list_transactions(address)

    def fetch_transactions(self, address, endblock=None, verbose=False):
        while True:
            
            startblock = self.latest_block(address)
            if verbose:
                if startblock is None:
                    print('startblock is None')
                else:
                    print('startblock', startblock)
                
            transactions = self.fetch_transactions_in_range(address, startblock, endblock)
            self.insert_transactions(address, transactions)
            
            if len(transactions) < 10000:
                if verbose:
                    print('done', len(transactions), 'transactions')
                break
            else:
                print('loaded', len(transactions), 'transactions')
    
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