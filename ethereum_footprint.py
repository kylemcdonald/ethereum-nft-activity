import datetime
from utils import read_csv
from collections import defaultdict
import requests
import pandas as pd
from etherscan import wei_to_eth
from ethereum_stats import EthereumStats
from nearest_dict import NearestDict

daily_ktco2_url = 'https://kylemcdonald.github.io/ethereum-emissions/output/daily-ktco2.csv'

class EthereumFootprint():
    """
    Load the emissions estimate from ethereum-emissions, and
    load stats from Etherscan.
    """
    def __init__(self):
        self.stats = EthereumStats()

        rows = pd.read_csv(daily_ktco2_url)
        cols = ['Date','best']
        self.date_to_ktco2 = {}
        for date, value in rows[cols].values:
            date = pd.to_datetime(date).date()
            self.date_to_ktco2[date] = value
        self.date_to_ktco2 = NearestDict(self.date_to_ktco2)

    def sum_kgco2(self, transactions):
        fees_by_day = defaultdict(float)
        for tx in transactions:
            date = tx.get_datetime().date()
            fees_by_day[date] += tx.get_fees()
        ktco2 = 0
        for date, fees in fees_by_day.items():
            portion = wei_to_eth(fees) / self.stats.tx_fees[date]
            ktco2 += portion * self.date_to_ktco2[date]
        kgco2 = ktco2 * 1e6 # convert kilotons to kilograms
        return kgco2