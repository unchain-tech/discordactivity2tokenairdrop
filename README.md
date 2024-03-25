# CHAI distributor

This script consists of two parts:

1. Discord crawler
2. CHAI distribution CSV generator

The first part (`crawl_discordServer.sh`) crawls the UNCHAIN discord server and collects a dataset of chatlogs from specified channels within the specified timeframe.

The second part (`CHAIcounter.py`) looks into the collected dataset and counts the number of P2P reactions to UNCHAIN crew's posts, counts the amount of CHAI to give each individual, and generates a CSV file to be used in the Gnosis token [multisender app](https://github.com/bh2smith/safe-airdrop).

`CHAI_csv_execute.sh` runs both in sequence for convenience. It should be ran every week on Sundays.

## Must fix

- [CHAI form](https://airtable.com/shrlc6B8wfHBiZmYV) のアクセスを現在持っていないので配布に必要な discord->wallet アドレスの参照ができていない。同様のフォームを作り直し（カラム名 sensitive）、該当 API キーを更新する必要あり。

## Possible improvements

- github の secret をトラストするなら、safe の署名に用いる秘密鍵を格納しちゃって airdrop 自体を actions で cron job に投げられるかも（都度実行->safe で csv airdrop ポチポチしなくて良い）
