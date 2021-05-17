# ethereum-nft-activity

How much energy does it take to power popular Ethereum-backed CryptoArt platforms? And what emissions are associated with this energy use?

These questions do not have clear answers for two reasons:

1. The overall energy usage and emissions of Ethereum are hard to estimate. I am working on this in a separate repo: [kylemcdonald/ethereum-energy](https://github.com/kylemcdonald/ethereum-energy)
2. The portion for which a specific user, platform, or transaction might be considered "responsible" for is more of a philosophical question than a technical one. Like many complex systems, there is an indirect relationship between the service and the emissions. I am working on different approaches in this notebook: [Per-Transaction Models](https://github.com/kylemcdonald/cryptoart-footprint/blob/main/Per-Transaction%20Models.ipynb)

This table represents one method for computing emissions, as of April 29, 2021. The methodology is described below.

| Name          | Gas          | Transactions | kgCO2    |
|---------------|--------------|--------------|----------|
| Async         |   1638562820 |        16335 |   464189 |
| Foundation    |  20489990935 |       122582 | 10195179 |
| Known Origin  |   5129939934 |        21156 |  1696116 |
| Makersplace   |  24799705248 |        78510 |  7768245 |
| Nifty Gateway |  49791570029 |       202966 | 22253639 |
| OpenSea       | 217410494380 |      1016553 | 82838112 |
| Rarible       |  38112831226 |       293205 | 15496197 |
| SuperRare     |  18267224757 |       195806 |  6197049 |
| Zora          |   2317359284 |         9111 |  1091823 |

## Preparation

First, sign up for an API key at [Etherscan](https://etherscan.io/myapikey). Create `env.json` and add the API key. It should look like:

```json
{
    "etherscan-api-key": "<etherscan-api-key>"
}
```

Install dependencies:

```sh
pip install -r requirements.txt
```

Note: this project requires python3

### `contracts_footprint.py`

This will pull all the transactions from Etherscan, sum the gas and transaction counts, and do a basic emissions estimate. Results are saved in the `/output` directory as JSON or TSV. Run the script with, for example: `python contracts_footprint.py --verbose --tsv data/contracts.json data/nifty-gateway-contracts.json`. 

This may take longer the first time, while your local cache is updated. When updating after a week, it can take 5 minutes or more to download all new transactions. The entire cache can be multiple gigabytes. To reduce this cache size use the `--simplify` flag.

This script has a few unique additional flags:

* `--summary` to summarize the results in a format similar to the above table, combining multiple contracts into a single row of output.
* `--startdate` and `--enddate` can be used to only analyze a specific date range, using the format `YYYY-MM-DD`.
* `--tsv` will save the results of analysis as a TSV file instead of JSON.

### `contracts_history.py`

This will pull all the transactions from Etherscan, sum the transaction fees and gas used, and group by day and platform. Results are saved in the `/output` directory as CSV files. Run the script with, for example: `python contracts_history.py --verbose data/contracts.json data/nifty-gateway-contracts.json`

The most recent results are cached here:

- [Transaction fees](https://github.com/kylemcdonald/cryptoart-footprint/blob/main/output/cryptoart-fees.csv)
- [Gas usage](https://github.com/kylemcdonald/cryptoart-footprint/blob/main/output/cryptoart-gas.csv)

### Additional flags

Both scripts have these shared additional flags:

* `--noupdate` runs from cached results. This will not make any requests to Nifty Gateway or Etherscan. When using the `Etherscan` class in code without an API key, this is the default behavior.
* `--verbose` prints progress when scraping Nifty Gateway or pulling transactions from Etherscan.

### Helper scripts

* `python ethereum_stats.py` will pull stats from Etherscan like daily fees and block rewards and save them to `data/ethereum-stats.json`
* `python nifty_gateway.py` will scrape all the contracts from Nifty Gateway and save them to `data/nifty-gateway-contracts.json`

## Methodology

The footprint of a platform is the sum of the footprints for all artwork on the platform. Most platforms use a few Ethereum contracts to handle all artworks. For each contract, we download all the transactions associated with the contract from Etherscan. Then for each transaction, we compute the kgCO2/gas footprint for that day, based on three values:

1. The emissions intensity in kgCO2/kWh for the entire Ethereum network. This is an average of the emissions intensity for each mining pool in 2019, weighted by their percentage of the hashrate.
2. The total power used during that day, estimated by [Digiconomist](https://digiconomist.net/ethereum-energy-consumption/).
3. The total gas used during that day, measured by [Etherscan](https://etherscan.io/chart/gasused?output=csv).

The total kgCO2 for a platform is equal to the sum of the gas used for each transaction times the kgCO2/gas on that day. Finally, we add 20% to handle "network inefficiencies and unnaccounted for mining pools" [as originally described by Offsetra](https://www.notion.so/Carbon-FYI-Methodology-51e2d8c41d1c4963970a143b8629f5f9). Offsetra has since removed this 20% from their method.

## Sources

Contracts are sourced from a combination of personal research and [DappRadar](https://dappradar.com/).

When possible, we have confirmed contract coverage directly with the marketplaces. Confirmed contracts include:

* SuperRare: all confirmed
* Foundation: all confirmed
* OpenSea: some contracts on DappRadar have not been confirmed
* Nifty Gateway: all confirmed

### Limitations

* Digiconomist's Bitcoin estimates [have been criticized](https://www.coincenter.org/estimating-bitcoin-electricity-use-a-beginners-guide/) as low (5x too low) or high (2x too high) compared to other estimates. It may be possible to make a more accurate estimate for Ethereum following a different methodology, based on the available mining hardware and corresponding power usage. That said, even the official Ethereum website [references Digiconomist](https://ethereum.org/en/nft/#footnotes-and-sources) when discussing the power usage. Work on a more accurate bottom-up energy and emissions estimate for Ethereum is happening in [kylemcdonald/ethereum-energy](https://github.com/kylemcdonald/ethereum-energy).
* Mining pool locations and the corresponding emissions intensity may have changed significantly from the 2019 values. A full correction might correspond to a +/-50% change.

## How to add more platforms

To modify this code so that it works with more platforms, add every possible contract and wallet for each platform to the `data/contracts.json` file, using the format:

```js
'<Platform Name>/<Contract Name>': '<0xAddress>'
```

Additionally, any NFT-specific contracts (e.g. ERC-721 and compatible) should be added to the `data/marketplaces-collectibles-games.json` file, with a similar format.

Then [submit a pull request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request) back to this repository. Thanks in advance!

To track Cryptokitties, you will need to explicitly remove the Cryptokitties contract from the blocklist in `etherscan.py`. Cryptokitties are blocked by default because there is a collection of Momo Wang Cryptokitties that have been grafted onto the Nifty Gateway marketplace that would otherwise require this script to pull all Cryptokitties ever.

## Contracts and Addresses

Contracts and addresses used by each platform can be found in `data/contracts.json` and are also listed here using `python print_contracts.py` to generate Markdown. Nifty Gateway contracts are listed separately in `data/nifty-gateway-contracts.json`.

### Art Blocks

* [Deployer](https://etherscan.io/address/0x96dc73c8b5969608c77375f085949744b5177660) 2020-11-27 to 2021-05-15
* [GenArt721](https://etherscan.io/address/0x059EDD72Cd353dF5106D2B9cC5ab83a52287aC3a) 2020-11-27 to 2021-05-16
* [GenArt721Core](https://etherscan.io/address/0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270) 2020-12-12 to 2021-05-17

### Async

* [ASYNC](https://etherscan.io/address/0x6c424c25e9f1fff9642cb5b7750b0db7312c29ad) 2020-02-25 to 2021-05-02
* [ASYNC-V2](https://etherscan.io/address/0xb6dae651468e9593e4581705a09c10a76ac1e0c8) 2020-07-21 to 2021-05-03

### Foundation

* [ERC-721](https://etherscan.io/address/0xcda72070e455bb31c7690a170224ce43623d0b6f) 2021-01-13 to 2021-05-03
* [FND NFT (FNDNFT) ERC-20](https://etherscan.io/address/0x3b3ee1931dc30c1957379fac9aba94d1c48a5405) 2021-01-13 to 2021-05-03

### KnownOrigin

* [ArtistAcceptingBids](https://etherscan.io/address/0x921ade9018eec4a01e41e80a7eeba982b61724ec) 2018-10-23 to 2020-11-13
* [ArtistAcceptingBidsV2](https://etherscan.io/address/0x848b0ea643e5a352d78e2c0c12a2dd8c96fec639) 2019-02-26 to 2021-05-03
* [ArtistEditionControls](https://etherscan.io/address/0x06c741e6df49d7fda1f27f75fffd238d87619ba1) 2018-11-07 to 2020-07-07
* [ArtistEditionControlsV2](https://etherscan.io/address/0x5327cf8b4127e81013d706330043e8bf5673f50d) 2019-02-26 to 2021-05-03
* [KnownOrigin Token](https://etherscan.io/address/0xfbeef911dc5821886e1dda71586d90ed28174b7d) 2018-09-04 to 2021-05-03
* [KnownOriginDigitalAsset](https://etherscan.io/address/0xdde2d979e8d39bb8416eafcfc1758f3cab2c9c72) 2018-04-04 to 2021-04-18
* [SelfServiceAccessControls](https://etherscan.io/address/0xec133df5d806a9069aee513b8be01eeee2f03ff0) 2019-04-25 to 2021-05-02
* [SelfServiceEditionCuration](https://etherscan.io/address/0x8ab96f7b6c60df169296bc0a5a794cae90493bd9) 2019-04-08 to 2020-07-07
* [SelfServiceEditionCurationV2](https://etherscan.io/address/0xff043a999a697fb1efdb0c18fd500eb7eab4e846) 2019-04-25 to 2020-07-07
* [SelfServiceEditionCurationV3](https://etherscan.io/address/0x50782a63b7735483be07ef1c72d6d75e94b4a8f6) 2019-04-30 to 2020-07-07

### Makersplace

* [DigitalMediaCore](https://etherscan.io/address/0x2a46f2ffd99e19a89476e2f62270e0a35bbf0756) 2019-03-11 to 2021-05-03
* [Unknown 1](https://etherscan.io/address/0x3981a1218a95becb4258305584bf2f24ff8dedf2) 2019-02-26 to 2020-07-29
* [Unknown 2](https://etherscan.io/address/0x0ba51d9c015a7544e3560081ceb16ffe222dd64f) 2020-02-24 to 2021-05-01

### Nifty Gateway

* [GUSD cashout](https://etherscan.io/address/0x3e6722f32cbe5b3c7bd3dca7017c7ffe1b9e5a2a) 2020-01-31 to 2021-05-02

### OpenSea

* [OpenSea Shared Storefront (OPENSTORE)](https://etherscan.io/address/0x495f947276749ce646f68ac8c248420045cb7b5e) 2020-12-02 to 2021-05-03
* [OpenSea Token (OPT)](https://etherscan.io/address/0x1129eb10812935593bf44fe0a9b62a59a9202f6d) 2021-02-05 to 2021-04-29
* [OpenSeaENSResolver](https://etherscan.io/address/0x9c4e9cce4780062942a7fe34fa2fa7316c872956) 2019-06-27 to 2020-07-03
* [SaleClockAuction](https://etherscan.io/address/0x1f52b87c3503e537853e160adbf7e330ea0be7c4) 2018-01-08 to 2021-03-04
* [Unknown 1](https://etherscan.io/address/0x23b45c658737b12f1748ce56e9b6784b5e9f3ff8) 2018-02-15 to 2020-06-18
* [Unknown 2](https://etherscan.io/address/0x78997e9e939daffe7eb9ed114fbf7128d0cfcd39) 2018-04-03 to 2019-07-14
* [Wallet](https://etherscan.io/address/0x5b3256965e7c3cf26e11fcaf296dfc8807c01073) 2018-01-02 to 2021-05-03
* [Wyvern Exchange](https://etherscan.io/address/0x7be8076f4ea4a4ad08075c2508e481d6c946d12b) 2018-06-12 to 2021-05-03
* [WyvernProxyRegistry](https://etherscan.io/address/0xa5409ec958c83c3f309868babaca7c86dcb077c1) 2018-06-12 to 2021-05-03

### Rarible

* [ERC1155Sale 1](https://etherscan.io/address/0x8c530a698b6e83d562db09079bc458d4dad4e6c5) 2020-05-27 to 2020-10-11
* [ERC1155Sale 2](https://etherscan.io/address/0x93f2a75d771628856f37f256da95e99ea28aafbe) 2020-09-03 to 2021-04-23
* [ERC721Sale](https://etherscan.io/address/0x131aebbfe55bca0c9eaad4ea24d386c5c082dd58) 2020-09-03 to 2021-01-22
* [Exchange V1](https://etherscan.io/address/0xcd4ec7b66fbc029c116ba9ffb3e59351c20b5b06) 2020-11-17 to 2021-05-03
* [MintableToken 1](https://etherscan.io/address/0xf79ab01289f85b970bf33f0543e41409ed2e1c1f) 2019-10-18 to 2021-03-06
* [MintableToken 2](https://etherscan.io/address/0x6a5ff3ceecae9ceb96e6ac6c76b82af8b39f0eb3) 2019-12-23 to 2021-04-29
* [MintableToken 3](https://etherscan.io/address/0x60f80121c31a0d46b5279700f9df786054aa5ee5) 2020-05-27 to 2021-05-03
* [RariToken](https://etherscan.io/address/0xfca59cd816ab1ead66534d82bc21e7515ce441cf) 2020-07-14 to 2021-05-03
* [RaribleToken](https://etherscan.io/address/0xd07dc4262bcdbf85190c01c996b4c06a461d2430) 2020-05-27 to 2021-05-03
* [TokenSale](https://etherscan.io/address/0xf2ee97405593bc7b6275682b0331169a48fedec7) 2019-10-24 to 2020-08-31
* [Unknown 1](https://etherscan.io/address/0xa5af48b105ddf2fa73cbaac61d420ea31b3c2a07) 2020-05-27 to 2020-09-12

### SuperRare

* [Bids](https://etherscan.io/address/0x2947f98c42597966a0ec25e92843c09ac17fbaa7) 2019-09-04 to 2021-05-03
* [SupeRare (SUPR)](https://etherscan.io/address/0x41a322b28d0ff354040e2cbc676f0320d8c8850d) 2018-04-01 to 2021-05-03
* [SuperRareV2 (SUPR)](https://etherscan.io/address/0xb932a70a57673d89f4acffbe830e8ed7f75fb9e0) 2019-09-04 to 2021-05-03
* [Unknown 1](https://etherscan.io/address/0x65b49f7aee40347f5a90b714be4ef086f3fe5e2c) 2020-12-05 to 2021-05-03
* [Unknown 2](https://etherscan.io/address/0x8c9f364bf7a56ed058fc63ef81c6cf09c833e656) 2020-12-05 to 2021-05-03

### Zora

* [Market](https://etherscan.io/address/0xe5bfab544eca83849c53464f85b7164375bdaac1) 2020-12-31 to 2020-12-31
* [Media (ZORA)](https://etherscan.io/address/0xabefbc9fd2f806065b4f3c237d4b59d9a97bcac7) 2020-12-31 to 2021-05-03
