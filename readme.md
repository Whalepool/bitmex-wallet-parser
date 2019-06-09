# Bitmex Wallet Parser by [@whalepoolbtc](https://t.me/whalepoolbtc) - https://whalepool.io

## About
A simple script to parse over your bitmex wallet history file and give you an overview of your account.

### Donations
Please be sure to just use the [bitmex whalepool affiliate link - http://bitmex.whalepool.io](http://bitmex.whalepool.io) to support [whalepool](https://t.me/whalepoolbtc)

# Instructions
- Install `python-devel` package on your machine
- Install pip requirements `sudo pip install -r requirements.pip`
- Go to [https://www.bitmex.com/app/wallet](https://www.bitmex.com/app/wallet) and click the 'save as CSV' on the top right.  - This will download 'Wallet History - YYYY-MM-DD.csv' file. Put this file in the same location as the python script.
- run `python3.6 bitmex-wallet-parser.py` and then view the folder once complete, a chart will be saved there.

```bash
# Simple trading returns, no balances present
python bitmex-wallet-parser.py
# Show balances
python bitmex-wallet-parser.py --showmoney

# Show your wallet aswell, so u can see deposit/withdrawals from your account
python bitmex-wallet-parser.py --show-wallet

# Show your affiliate balances
python bitmex-wallet-parser.py --show-affiliate

# Hide your trading performance
# Maybe just to show affiliate balances and nothing else ? 
python bitmex-wallet-parser.py --hide-trading 
python bitmex-wallet-parser.py --hide-trading  --show-affiliate
python bitmex-wallet-parser.py --hide-trading  --show-affiliate --showmoney
```


### Options & Arguments
You can enter various arguments to tailer the chart that is output.
The options are as follows:

| Argument | Description |
| -------- | ----------- |
| `-h, --help` | show this help message and exit |
| `--hide-wallet` | hide wallet / transaction data |
| `--hide-affiliate` | hide affiliate data |
| `--hide-trading` | hide trading data |
| `--private` | hide numerical values |



### Single Chart Examples

- Transaction history  -
	`python3.6 bitmex-wallet-parser.py --hide-affiliate --hide-trading`

- Affiliate income  -
	`python3.6 bitmex-wallet-parser.py --hide-wallet --hide-trading`

- Trading performance  -
	`python3.6 bitmex-wallet-parser.py --hide-wallet --hide-affiliate`

Add the `--private` flag on any command to remove values for more privacy when sharing your charts.

------

### Two Chart Examples

- Transaction history + Affiliate Income  -
	`python3.6 bitmex-wallet-parser.py --hide-trading`

- Transaction history + Trading performance  -
	`python3.6 bitmex-wallet-parser.py --hide-affiliate`

- Affiliate income + Trading performance  -
	`python3.6 bitmex-wallet-parser.py --hide-wallet`

Add the `--private` flag on any command to remove values for more privacy when sharing your charts.


------

### Three Chart Example

By default the script will produce 3 charts on the one image summarising your transaction + affiliate + trading performance

`python3.6 bitmex-wallet-parser.py`


For more info join [@whalepoolbtc](https://t.me/whalepoolbtc) on telegram
