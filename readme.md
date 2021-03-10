# cryptoart-footprint

Estimate the total CO2 footprint for popular CryptoArt platforms. The goal is to accurately quantify the ecological damage of Ethereum 1.0 PoW-backed CryptoArt platforms.

To estimate the footprint for a specific Ethereum wallet or contract (up to 10,000 transactions) try [carbon.fyi](https://carbon.fyi/). To estimate the footprint of a specific artwork try [cryptoart.wtf](http://cryptoart.wtf/).

Status as of March 9, 2021:

| Name          | Gas             | Transactions | kgCO2      |
|---------------|-----------------|--------------|------------|
| OpenSea       | 146,210,589,984 |      663,946 | 46,882,237 |
| Nifty Gateway |  22,692,781,162 |       82,920 |  8,638,915 |
| Rarible       |  21,336,740,026 |      169,149 |  7,032,924 |
| Makersplace   |  20,254,567,543 |       64,625 |  5,490,208 |
| SuperRare     |  14,816,160,348 |      160,293 |  4,449,347 |
| Foundation    |   3,650,433,860 |       23,003 |  1,782,331 |
| Known Origin  |   4,457,508,470 |       18,223 |  1,355,487 |
| Zora          |   1,399,949,616 |        5,231 |    626,492 |
| Async         |   1,439,494,155 |       14,523 |    363,991 |

## Run

First, sign up for an API key at [Etherscan](https://etherscan.io/myapikey). Create `env.json` and add the API key. It should look like:

```json
{
    "etherscan-api-key": "<etherscan-api-key>"
}
```

Install requests `pip install requests` if it is not already available.

Then run the script: `python cryptoart-footprint.py > footprint.tsv`

This may take longer the first time, while your local cache is updated.

Additional flags:

* `--ng` to also estimate the footprint for Nifty Gateway. This takes much longer than other platforms, because Nifty Gateway uses a separate smart contract per exhibition/drop.
* `--summary` to summarize the results in a format similar to the above table, combining multiple contracts into a single row of output.
* `--commas` to print the output with thousands comma separators.
* `--verbose` prints progress when scraping Nifty Gateway or pulling transactions from Etherscan. 

## Methodology

The footprint of a platform is the sum of the footprints for all artwork on the platform. Most platforms use a few Ethereum contracts to handle all artworks. For each contract, we download all the transactions associated with the contract from Etherscan. Then for each transaction, we compute the kgCO2/gas footprint for that day, based on three values:

1. The emissions intensity in kgCO2/kWh for the entire Ethereum network. This is an average of the emissions intensity for each mining pool in 2019, weighted by their percentage of the hashrate.
2. The total power used during that day, estimated by [Digiconomist](https://digiconomist.net/ethereum-energy-consumption/).
3. The total gas used during that day, measured by [Etherscan](https://etherscan.io/chart/gasused?output=csv).

The total kgCO2 for a platform is equal to the sum of the gas used for each transaction times the kgCO2/gas on that day. Finally, we add 20% to handle "network inefficiencies and unnaccounted for mining pools" [as described by Offsetra](https://www.notion.so/Carbon-FYI-Methodology-51e2d8c41d1c4963970a143b8629f5f9).

## Sources

When possible, we have confirmed contract coverage directly with the marketplaces. Confirmed contracts include:

* SuperRare
* Foundation

### Limitations

* Digiconomist's Bitcoin estimates [have been criticized](https://www.coincenter.org/estimating-bitcoin-electricity-use-a-beginners-guide/) as low (5x too low) or high (2x too high) compared to other estimates. It may be possible to make a more accurate estimate for Ethereum following a different methodology, based on the available mining hardware and corresponding power usage. That said, even the official Ethereum website [references Digiconomist](https://ethereum.org/en/nft/#footnotes-and-sources) when discussing the power usage.
* Mining pool locations and the corresponding emissions intensity may have changed significantly from the 2019 values. A full correction might correspond to a +/-50% change.
