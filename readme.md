# cryptoart-footprint

Estimate the total CO2 footprint for popular CryptoArt platforms. The goal is to accurately quantify the ecological damage of Ethereum 1.0 PoW-backed CryptoArt platforms.

To estimate the footprint for a specific Ethereum wallet or contract (up to 10,000 transactions) try [carbon.fyi](https://carbon.fyi/). To estimate the footprint of a specific artwork try [cryptoart.wtf](http://cryptoart.wtf/).

Status as of March 22, 2021:

| Name          | Gas             | Transactions | kgCO2      |
|---------------|-----------------|--------------|------------|
| OpenSea       | 173,618,258,189 |      804,476 | 60,962,694 |
| Nifty Gateway |  31,925,160,353 |      116,531 | 13,381,972 |
| Rarible       |  27,700,791,937 |      216,407 | 10,302,402 |
| Makersplace   |  21,679,291,384 |       69,165 |  6,222,148 |
| SuperRare     |  15,950,212,376 |      171,967 |  5,031,957 |
| Foundation    |   8,169,344,070 |       51,375 |  4,103,883 |
| Known Origin  |   4,677,980,129 |       19,181 |  1,468,752 |
| Zora          |   1,871,937,838 |        7,137 |    868,972 |
| Async         |   1,502,889,319 |       15,081 |    396,560 |

## Run

First, sign up for an API key at [Etherscan](https://etherscan.io/myapikey). Create `env.json` and add the API key. It should look like:

```json
{
    "etherscan-api-key": "<etherscan-api-key>"
}
```

Install requests `pip install requests` if it is not already available.

Then run the script: `python cryptoart_footprint.py > footprint.tsv`

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

## Contracts and Addresses

Contracts and addresses used by each platform can be found in `data/contracts.json` and are also listed here using `python print_contracts.py` to generate Markdown.

### Async

* [ASYNC](https://etherscan.io/address/0x6c424c25e9f1fff9642cb5b7750b0db7312c29ad)
* [ASYNC-V2](https://etherscan.io/address/0xb6dae651468e9593e4581705a09c10a76ac1e0c8)

### Foundation

* [ERC-721](https://etherscan.io/address/0xcda72070e455bb31c7690a170224ce43623d0b6f)
* [FND NFT (FNDNFT) ERC-20](https://etherscan.io/address/0x3b3ee1931dc30c1957379fac9aba94d1c48a5405)

### Known Origin

* [KnownOriginDigitalAsset (KODA)](https://etherscan.io/address/0xfbeef911dc5821886e1dda71586d90ed28174b7d)

### Makersplace

* [MakersTokenV2 (MKT2)](https://etherscan.io/address/0x2a46f2ffd99e19a89476e2f62270e0a35bbf0756)

### Nifty Gateway

Uses many separate contracts.

### OpenSea

* [OpenSea Shared Storefront (OPENSTORE)](https://etherscan.io/address/0x495f947276749ce646f68ac8c248420045cb7b5e)
* [OpenSea Token (OPT)](https://etherscan.io/address/0x1129eb10812935593bf44fe0a9b62a59a9202f6d)
* [OpenSeaENSResolver](https://etherscan.io/address/0x9c4e9cce4780062942a7fe34fa2fa7316c872956)
* [Wallet](https://etherscan.io/address/0x5b3256965e7c3cf26e11fcaf296dfc8807c01073)
* [Wyvern Exchange](https://etherscan.io/address/0x7be8076f4ea4a4ad08075c2508e481d6c946d12b)
* [WyvernProxyRegistry](https://etherscan.io/address/0xa5409ec958c83c3f309868babaca7c86dcb077c1)

### Rarible

* [MintableToken (RARI)](https://etherscan.io/address/0x60f80121c31a0d46b5279700f9df786054aa5ee5)
* [RariToken (RARI)](https://etherscan.io/address/0xfca59cd816ab1ead66534d82bc21e7515ce441cf)

### SuperRare

* [Bids](https://etherscan.io/address/0x2947f98c42597966a0ec25e92843c09ac17fbaa7)
* [SupeRare (SUPR)](https://etherscan.io/address/0x41a322b28d0ff354040e2cbc676f0320d8c8850d)
* [SuperRareV2 (SUPR)](https://etherscan.io/address/0xb932a70a57673d89f4acffbe830e8ed7f75fb9e0)
* [Unknown 1](https://etherscan.io/address/0x65b49f7aee40347f5a90b714be4ef086f3fe5e2c)
* [Unknown 2](https://etherscan.io/address/0x8c9f364bf7a56ed058fc63ef81c6cf09c833e656)

### Zora

* [Market](https://etherscan.io/address/0xe5bfab544eca83849c53464f85b7164375bdaac1)
* [Media (ZORA)](https://etherscan.io/address/0xabefbc9fd2f806065b4f3c237d4b59d9a97bcac7)