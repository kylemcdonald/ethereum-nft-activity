#!/bin/bash

# start on main
git checkout main

# update foundation contracts
python3 foundation.py

# update nifty gateway contracts
python3 nifty_gateway.py

# get the latest ethereum statistics
python3 ethereum_stats.py

# run the full history generation
python3 contracts_history.py \
    --prefix "nft" \
    --verbose \
    data/contracts.json \
    data/nifty-gateway-contracts.json \
    data/foundation-contracts.json \
    data/other-nft-dapps.json

# compute percentages
python3 compute_percentages.py nft

# make copy of files
mkdir -p backup
cp output/nft-* backup
git reset --hard
git checkout gh-pages
git checkout --orphan flattened
cp backup/nft-* output/
rm -rf backup
git add .
git commit -m "update"
git push origin +flattened:gh-pages
git checkout main