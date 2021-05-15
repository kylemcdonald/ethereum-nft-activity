#!/bin/bash

# start on main
git checkout main

# update nifty gateway contracts
python3 nifty_gateway.py

# get the latest ethereum statistics
python3 ethereum_stats.py

# run the full history generation
python3 contracts_history.py \
    --prefix "nft" \
    --verbose \
    data/nifty-gateway-contracts.json \
    data/marketplaces-collectibles-games.json

# compute percentages
python3 compute_percentages.py nft

# make copy of files
mkdir -p backup
cp output/nft-* backup
git reset --hard
git checkout gh-pages
cp backup/nft-* output/
git add -u output/
git commit -m "update"
git push origin gh-pages
git checkout main