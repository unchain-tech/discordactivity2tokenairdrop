# CHAI distributor

This script consists of two parts:

1. Discord cralwer
2. CHAI distribution CSV generator

The first part (`crawl_discordServer.sh`) crawls the UNCHAIN discord server and collects a dataset of chatlogs from specified channels within the specified timeframe.


The second part (`CHAIcounter.py`) looks into the collected dataset and counts the number of P2P reactions to UNCHAIN crew's posts, counts the amount of CHAI to give each individual, and generates a CSV file to be used in the Gnosis token [multisender app](https://github.com/bh2smith/safe-airdrop).

`CHAI_csv_execute.sh` runs both in sequence for convenience. It should be ran every week on Sundays.