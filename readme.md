# ethereum-nft-activity

How much energy does it take to power popular Ethereum-backed CryptoArt platforms? And what emissions are associated with this energy use?

These questions do not have clear answers for two reasons:

1. The overall energy usage and emissions of Ethereum are hard to estimate. I am working on this in a separate repo: [kylemcdonald/ethereum-energy](https://github.com/kylemcdonald/ethereum-energy)
2. The portion for which a specific user, platform, or transaction might be considered "responsible" is more of a philosophical question than a technical one. Like many complex systems, there is an indirect relationship between the service and the emissions. I am working on different approaches in this notebook: [Per-Transaction Models](https://github.com/kylemcdonald/cryptoart-footprint/blob/main/Per-Transaction%20Models.ipynb)

This table represents one method for computing emissions, as of January 9, 2022. The methodology is described below.

| Name          | Fees      | Transactions | kgCO2     | 
|---------------|-----------|--------------|-----------| 
| Art Blocks    | 713.27    | 91861        | 1227523   | 
| Async         | 209.69    | 26193        | 303379    | 
| Foundation    | 7271.77   | 555013       | 12014180  | 
| KnownOrigin   | 495.10    | 62940        | 877928    | 
| Makersplace   | 1677.60   | 112881       | 2652522   | 
| Nifty Gateway | 28146.03  | 1007846      | 43488939  | 
| OpenSea       | 210924.13 | 14327923     | 359530331 | 
| Rarible       | 20428.42  | 1755633      | 26793381  | 
| SuperRare     | 1895.23   | 274409       | 2625774   | 
| Zora          | 476.93    | 19547        | 616433    | 


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

Note: this project requires Python 3.

### `contracts_footprint.py`

This will pull all the transactions from Etherscan, sum the gas and transaction counts, and do a basic emissions estimate. Results are saved in the `/output` directory as JSON or TSV. Run the script with, for example: `python contracts_footprint.py --verbose --tsv data/contracts.json data/nifty-gateway-contracts.json`. 

This may take longer the first time, while your local cache is updated. When updating after a week, it can take 5 minutes or more to download all new transactions. The entire cache can be multiple gigabytes.

This script has a few unique additional flags:

* `--summary` to summarize the results in a format similar to the above table, combining multiple contracts into a single row of output.
* `--startdate` and `--enddate` can be used to only analyze a specific date range, using the format `YYYY-MM-DD`.
* `--tsv` will save the results of analysis as a TSV file instead of JSON.

### `contracts_history.py`

This will pull all the transactions from Etherscan, sum the transaction fees and gas used, and group by day and platform. Results are saved in the `/output` directory as CSV files. Run the script with, for example: `python contracts_history.py --verbose data/contracts.json data/nifty-gateway-contracts.json`

The most recent results are [cached in the gh_pages branch](https://github.com/kylemcdonald/ethereum-nft-activity/tree/gh-pages/output).

### Additional flags

Both scripts have these shared additional flags:

* `--noupdate` runs from cached results. This will not make any requests to Nifty Gateway or Etherscan. When using the `Etherscan` class in code without an API key, this is the default behavior.
* `--verbose` prints progress when scraping Nifty Gateway or pulling transactions from Etherscan.

### Helper scripts

* `python ethereum_stats.py` will pull stats from Etherscan like daily fees and block rewards and save them to `data/ethereum-stats.json`
* `python nifty_gateway.py` will scrape all the contracts from Nifty Gateway and save them to `data/nifty-gateway-contracts.json`

## Methodology

The footprint of a platform is the sum of the footprints for all artwork on the platform. Most platforms use a few Ethereum contracts and addresses to handle all artworks. For each contract, we download all the transactions associated with that address from Etherscan. Then for each day, we take the sum of all fees paid on all those transactions divided by the total fees paid across the whole network for that day. This ratio is multiplied by the daily [Ethereum emissions estimate](https://github.com/kylemcdonald/ethereum-emissions) to get the total emissions for that address. Finally, the total emissions for a platform are equal to the emissions for all addresses across all days.

## Sources

Contracts are sourced from a combination of personal research, [DappRadar](https://dappradar.com/), and [Etherscan](https://etherscan.io/) tags.

When possible, we have confirmed contract coverage directly with the marketplaces. Confirmed contracts include:

* SuperRare: all confirmed
* Foundation: all confirmed
* OpenSea: some contracts on DappRadar have not been confirmed
* Nifty Gateway: all confirmed

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

* [Deployer](https://etherscan.io/address/0x96dc73c8b5969608c77375f085949744b5177660) 2020-11-26 to 2021-08-13
* [GenArt721](https://etherscan.io/address/0x059EDD72Cd353dF5106D2B9cC5ab83a52287aC3a) 2020-11-26 to 2022-01-09
* [GenArt721Core](https://etherscan.io/address/0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270) 2020-12-12 to 2022-01-09

### Async

* [ASYNC](https://etherscan.io/address/0x6c424c25e9f1fff9642cb5b7750b0db7312c29ad) 2020-02-25 to 2021-12-21
* [ASYNC-V2](https://etherscan.io/address/0xb6dae651468e9593e4581705a09c10a76ac1e0c8) 2020-07-21 to 2022-01-09

### Foundation

* [ERC-721](https://etherscan.io/address/0xcda72070e455bb31c7690a170224ce43623d0b6f) 2021-01-13 to 2022-01-09
* [FND NFT (FNDNFT) ERC-20](https://etherscan.io/address/0x3b3ee1931dc30c1957379fac9aba94d1c48a5405) 2021-01-13 to 2022-01-09

### KnownOrigin

* [ArtistAcceptingBids](https://etherscan.io/address/0x921ade9018eec4a01e41e80a7eeba982b61724ec) 2018-10-23 to 2020-11-13
* [ArtistAcceptingBidsV2](https://etherscan.io/address/0x848b0ea643e5a352d78e2c0c12a2dd8c96fec639) 2019-02-26 to 2022-01-07
* [ArtistEditionControls](https://etherscan.io/address/0x06c741e6df49d7fda1f27f75fffd238d87619ba1) 2018-11-07 to 2020-07-07
* [ArtistEditionControlsV2](https://etherscan.io/address/0x5327cf8b4127e81013d706330043e8bf5673f50d) 2019-02-26 to 2022-01-09
* [KnownOrigin Token](https://etherscan.io/address/0xfbeef911dc5821886e1dda71586d90ed28174b7d) 2018-09-04 to 2022-01-09
* [KnownOriginDigitalAsset](https://etherscan.io/address/0xdde2d979e8d39bb8416eafcfc1758f3cab2c9c72) 2018-04-04 to 2021-12-21
* [SelfServiceAccessControls](https://etherscan.io/address/0xec133df5d806a9069aee513b8be01eeee2f03ff0) 2019-04-25 to 2021-08-23
* [SelfServiceEditionCuration](https://etherscan.io/address/0x8ab96f7b6c60df169296bc0a5a794cae90493bd9) 2019-04-08 to 2020-07-07
* [SelfServiceEditionCurationV2](https://etherscan.io/address/0xff043a999a697fb1efdb0c18fd500eb7eab4e846) 2019-04-25 to 2020-07-07
* [SelfServiceEditionCurationV3](https://etherscan.io/address/0x50782a63b7735483be07ef1c72d6d75e94b4a8f6) 2019-04-30 to 2020-07-07

### Makersplace

* [DigitalMediaCore](https://etherscan.io/address/0x2a46f2ffd99e19a89476e2f62270e0a35bbf0756) 2019-03-11 to 2022-01-09
* [Unknown 1](https://etherscan.io/address/0x3981a1218a95becb4258305584bf2f24ff8dedf2) 2019-02-26 to 2020-07-29
* [Unknown 2](https://etherscan.io/address/0x0ba51d9c015a7544e3560081ceb16ffe222dd64f) 2020-02-24 to 2022-01-08

### Nifty Gateway

* Many individual contracts defined in `data/nifty-gateway-contracts.json`
* [Builder Shop](https://etherscan.io/address/0x431bd1297a1c7664d599364a427a2d926a1f58ae) 2020-03-21 to 2021-07-27
* [First and Last](https://etherscan.io/address/0x11ab0243c57c6c1b39f2908aaebaed7ccf351491) 2021-03-13 to 2022-01-09
* [GUSD cashout](https://etherscan.io/address/0x3e6722f32cbe5b3c7bd3dca7017c7ffe1b9e5a2a) 2020-01-31 to 2022-01-09
* [Getaway Auctions](https://etherscan.io/address/0xf72136fb50f0c90324c9619aaab4289eeb277f3e) 2021-03-15 to 2021-12-06
* [Hard To Explain](https://etherscan.io/address/0xef2883efa7bf4ecf169f3ad6c012994078608985) 2021-03-14 to 2022-01-07
* [Insides](https://etherscan.io/address/0x934fdb5084d448de4c61c960c5f806689ae720b1) 2021-03-14 to 2022-01-04
* [Omnibus](https://etherscan.io/address/0xe052113bd7d7700d623414a0a4585bcae754e9d5) 2020-01-31 to 2022-01-09

### OpenSea

* [OpenSea Shared Storefront (OPENSTORE)](https://etherscan.io/address/0x495f947276749ce646f68ac8c248420045cb7b5e) 2020-12-02 to 2022-01-09
* [OpenSea Token (OPT)](https://etherscan.io/address/0x1129eb10812935593bf44fe0a9b62a59a9202f6d) 2021-02-05 to 2021-04-29
* [OpenSeaENSResolver](https://etherscan.io/address/0x9c4e9cce4780062942a7fe34fa2fa7316c872956) 2019-06-27 to 2020-07-03
* [SaleClockAuction](https://etherscan.io/address/0x1f52b87c3503e537853e160adbf7e330ea0be7c4) 2018-01-08 to 2021-10-18
* [Unknown 1](https://etherscan.io/address/0x23b45c658737b12f1748ce56e9b6784b5e9f3ff8) 2018-02-15 to 2020-06-18
* [Unknown 2](https://etherscan.io/address/0x78997e9e939daffe7eb9ed114fbf7128d0cfcd39) 2018-04-03 to 2021-08-16
* [Wallet](https://etherscan.io/address/0x5b3256965e7c3cf26e11fcaf296dfc8807c01073) 2018-01-02 to 2022-01-09
* [Wyvern Exchange](https://etherscan.io/address/0x7be8076f4ea4a4ad08075c2508e481d6c946d12b) 2018-06-12 to 2022-01-09
* [WyvernProxyRegistry](https://etherscan.io/address/0xa5409ec958c83c3f309868babaca7c86dcb077c1) 2018-06-12 to 2022-01-09

### Rarible

* [Asset Contract ERC1155](https://etherscan.io/address/0xb66a603f4cfe17e3d27b87a8bfcad319856518b8) 2021-06-11 to 2022-01-09
* [Asset Contract ERC721](https://etherscan.io/address/0xf6793da657495ffeff9ee6350824910abc21356c) 2021-06-11 to 2022-01-09
* [Deployer](https://etherscan.io/address/0x3482549fca7511267c9ef7089507c0f16ea1dcc1) 2018-10-08 to 2021-12-16
* [ERC1155 Factory](https://etherscan.io/address/0x81243681078bee8e251d02ee6872b1eaa6dd982a) 2021-08-05 to 2021-12-09
* [ERC1155 Sale 1](https://etherscan.io/address/0x8c530a698b6e83d562db09079bc458d4dad4e6c5) 2020-05-27 to 2020-10-11
* [ERC1155 Sale 2](https://etherscan.io/address/0x93f2a75d771628856f37f256da95e99ea28aafbe) 2020-09-03 to 2021-06-05
* [ERC721 Factory](https://etherscan.io/address/0x6d9dd3547baf4c190ab89e0103c363feaf325eca) 2021-08-05 to 2021-10-22
* [ERC721 Sale](https://etherscan.io/address/0x131aebbfe55bca0c9eaad4ea24d386c5c082dd58) 2020-09-03 to 2021-01-22
* [Exchange 1](https://etherscan.io/address/0xcd4ec7b66fbc029c116ba9ffb3e59351c20b5b06) 2020-11-17 to 2022-01-05
* [Exchange Proxy](https://etherscan.io/address/0x9757f2d2b135150bbeb65308d4a91804107cd8d6) 2021-06-11 to 2022-01-09
* [External Royalties](https://etherscan.io/address/0xea90cfad1b8e030b8fd3e63d22074e0aeb8e0dcd) 2021-06-18 to 2022-01-09
* [MintableToken 1](https://etherscan.io/address/0xf79ab01289f85b970bf33f0543e41409ed2e1c1f) 2019-10-18 to 2021-10-17
* [MintableToken 2](https://etherscan.io/address/0x6a5ff3ceecae9ceb96e6ac6c76b82af8b39f0eb3) 2019-12-23 to 2022-01-06
* [MintableToken 3](https://etherscan.io/address/0x60f80121c31a0d46b5279700f9df786054aa5ee5) 2020-05-27 to 2022-01-09
* [RARI Token 1](https://etherscan.io/address/0xfca59cd816ab1ead66534d82bc21e7515ce441cf) 2020-07-14 to 2022-01-09
* [RARI Token 2](https://etherscan.io/address/0x60f80121c31a0d46b5279700f9df786054aa5ee5) 2020-05-27 to 2022-01-09
* [RaribleToken](https://etherscan.io/address/0xd07dc4262bcdbf85190c01c996b4c06a461d2430) 2020-05-27 to 2022-01-09
* [TokenSale](https://etherscan.io/address/0xf2ee97405593bc7b6275682b0331169a48fedec7) 2019-10-24 to 2020-08-31
* [Treasury](https://etherscan.io/address/0x1cf0df2a5a20cd61d68d4489eebbf85b8d39e18a) 2021-01-07 to 2021-12-09
* [Unknown 1](https://etherscan.io/address/0xa5af48b105ddf2fa73cbaac61d420ea31b3c2a07) 2020-05-27 to 2020-09-12

### SuperRare

* [Bids](https://etherscan.io/address/0x2947f98c42597966a0ec25e92843c09ac17fbaa7) 2019-09-04 to 2021-12-31
* [SupeRare (SUPR)](https://etherscan.io/address/0x41a322b28d0ff354040e2cbc676f0320d8c8850d) 2018-04-01 to 2022-01-09
* [SuperRareV2 (SUPR)](https://etherscan.io/address/0xb932a70a57673d89f4acffbe830e8ed7f75fb9e0) 2019-09-04 to 2022-01-09
* [Unknown 1](https://etherscan.io/address/0x65b49f7aee40347f5a90b714be4ef086f3fe5e2c) 2020-12-05 to 2022-01-09
* [Unknown 2](https://etherscan.io/address/0x8c9f364bf7a56ed058fc63ef81c6cf09c833e656) 2020-12-05 to 2022-01-09

### Zora

* [Market](https://etherscan.io/address/0xe5bfab544eca83849c53464f85b7164375bdaac1) 2020-12-31 to 2020-12-31
* [Media (ZORA)](https://etherscan.io/address/0xabefbc9fd2f806065b4f3c237d4b59d9a97bcac7) 2020-12-31 to 2022-01-09