# cryptoart-emissions

Estimate the total emissions for popular CryptoArt platforms. The goal is to accurately quantify the ecological damage of Ethereum 1.0 PoW-backed CryptoArt platforms.

To estimate the emissions for a specific Ethereum wallet or contract (up to 10,000 transactions) try [carbon.fyi](https://carbon.fyi/). To estimate the emissions of a specific artwork try [cryptoart.wtf](http://cryptoart.wtf/).

Status as of March 8, 2021:

| Platform      	| Gas             	| Transactions 	| kgCO2      	|
|---------------	|-----------------	|--------------	|------------	|
| OpenSea       	| 118,073,445,239 	|      578,544 	| 36,707,068 	|
| Nifty Gateway 	|  22,066,205,976 	|       80,700 	|  8,317,022 	|
| Rarible       	|  20,411,193,512 	|      162,029 	|  6,557,432 	|
| Makersplace   	|  20,078,928,528 	|       64,120 	|  5,399,975 	|
| SuperRare     	|  13,472,934,875 	|      147,350 	|  3,875,325 	|
| Foundation    	|   3,209,093,544 	|       20,035 	|  1,555,597 	|
| Known Origin  	|   4,430,475,709 	|       18,107 	|  1,341,599 	|
| Zora          	|   1,308,250,027 	|        4,840 	|    579,382 	|
| Async         	|   1,413,074,027 	|       14,400 	|    350,418 	|

## Run

First, sign up for an API key at Etherscan. Add the API key to `env.json`. Install requests `pip install requests` if it is not already available.

Then run the script: `python cryptoart-emissions.py > emissions.tsv`

This may take longer the first time, while your local cache is updated.

To also estimate the emissions for Nifty Gateway, add the `--ng` flag. This takes much longer than other platforms, because Nifty Gateway uses a separate smart contract per exhibition/drop.

## Methodology

The emissions of a platform is the sum of the emissions for all artwork on the platform. Most platforms use a few Ethereum contracts to handle all artworks. For each contract, we download all the transactions associated with the contract from Etherscan. Then for each transaction, we compute the kgCO2/gas emissions for that day, based on three values:

1. The emissions intensity in kgCO2/kWh for the entire Ethereum network. This is an average of the emissions intensity for each mining pool in 2019, weighted by their percentage of the hashrate.
2. The total power used during that day, estimated by [Digiconomist](https://digiconomist.net/ethereum-energy-consumption/).
3. The total gas used during that day, measured by [Etherscan](https://etherscan.io/chart/gasused?output=csv).

The total kgCO2 for a platform is equal to the sum of the gas used for each transaction times the kgCO2/gas on that day. Finally, we add 20% to handle "network inefficiencies and unnaccounted for mining pools" [as described by Offsetra](https://www.notion.so/Carbon-FYI-Methodology-51e2d8c41d1c4963970a143b8629f5f9).

### Limitations

* Digiconomist's Bitcoin estimates [have been criticized](https://www.coincenter.org/estimating-bitcoin-electricity-use-a-beginners-guide/) as low (5x too low) or high (2x too high) compared to other estimates. It may be possible to make a more accurate estimate for Ethereum following a different methodology, based on the available mining hardware and corresponding power usage. That said, even the official Ethereum website [references Digiconomist](https://ethereum.org/en/nft/#footnotes-and-sources) when discussing the power usage.
* Mining pool locations and the corresponding emissions intensity may have changed significantly from the 2019 values. A full correction might correspond to a +/-50% change.
