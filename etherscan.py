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

def addr(address):
    return f'"{address.lower()}"'

class Etherscan():
    def __init__(self, apikey=None, db_file='transactions.sqlite3', read_only=False):
        self.apikey = apikey
        flags = '?mode=ro' if read_only else ''
        self.db = sqlite3.connect(f'file:{db_file}{flags}', uri=True)

    def __del__(self):
        self.db.close()
    
    def execute(self, query):
        return self.db.cursor().execute(query)

    def list_contracts(self):
        query = 'SELECT name FROM sqlite_master WHERE type="table"'
        for row in self.execute(query):
            yield row[0]
    
    def insert_transactions(self, address, transactions):
        query = f'INSERT OR REPLACE INTO {addr(address)} VALUES (?, ?, ?, ?, ?)'
        self.db.cursor().executemany(query, build_rows(transactions))
        
    def create_transactions_table(self, address):
        return self.execute(
            f'CREATE TABLE IF NOT EXISTS {addr(address)} (\
            hash BLOB PRIMARY KEY, \
            block_number INTEGER KEY, \
            timestamp INTEGER, \
            gas_price INTEGER, \
            gas_used INTEGER)')
    
    def list_transactions(self, address):
        query = f'SELECT * FROM {addr(address)}'
        for row in self.execute(query):
            yield Transaction(*row)

    def count_transactions(self, address):
        query = f'SELECT COUNT(*) FROM {addr(address)}'
        return self.execute(query).fetchone()[0]

    def latest_transaction(self, address):
        query = f'SELECT * FROM {addr(address)} ORDER BY timestamp DESC LIMIT 1'
        row = self.execute(query).fetchone()
        if row is not None:
            return Transaction(*row)

    def latest_datetime(self, address):
        query = f'SELECT MAX(timestamp) FROM {addr(address)}'
        timestamp = self.execute(query).fetchone()[0]
        if timestamp is not None:
            return datetime.datetime.fromtimestamp(timestamp)

    def latest_block(self, address):
        query = f'SELECT MAX(block_number) FROM {addr(address)}'
        return self.execute(query).fetchone()[0]

    def load_transactions(self, address, update=True, update_active=None, verbose=False, **kwargs):
        if self.apikey is None:
            update = False
        if verbose:
            print('load_transactions', address)
        self.create_transactions_table(address)   
        if update_active is not None:
            now = datetime.datetime.now()
            latest = self.latest_datetime(address)
            if latest is not None:
                seconds_per_day = 24 * 60 * 60
                days = (now - latest).total_seconds() / seconds_per_day
                update = days < update_active
                if verbose:
                    print(f'latest transaction {days:.1f} day(s) ago')
        if not update:
            return self.list_transactions(address)
        self.fetch_transactions(address, verbose=verbose, **kwargs)
        return self.list_transactions(address)

    def fetch_transactions(self, address, endblock=None, verbose=False):
        last_startblock = None
        while True:
            startblock = self.latest_block(address)

            # quit if we have a block, but haven't made progress
            if startblock is not None and startblock == last_startblock:
                if verbose:
                    print('done')
                break

            if verbose:
                if startblock is None:
                    print('startblock is None')
                else:
                    print('startblock', startblock)
            
            transactions = self.fetch_transactions_in_range(address, startblock, endblock)
            self.insert_transactions(address, transactions)

            if verbose:
                print(f'loaded {len(transactions)} transactions')

            last_startblock = startblock
        self.db.commit()
    
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