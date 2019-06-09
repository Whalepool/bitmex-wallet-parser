# Bitmex Wallet Parser by [@whalepoolbtc](https://t.me/whalepoolbtc) - https://whalepool.io

## About
A simple script to parse over your bitmex wallet history file and give you an overview of your account.

### Support
Please use the [bitmex whalepool affiliate link](http://bitmex.whalepool.io) or the [deribit whalepool affiliate link](http://derbit.whalepool.io) to support [@whalepool](https://t.me/whalepoolbtc)

# Install / Setup Instructions
- Install `python-devel` package on your machine
- Install pip requirements:
	- **Linux** `sudo pip install -r requirements.pip`
	- **Windows** `py pip install -r requirements.pip`

## Use via downloading your bitmex wallet history as .csv file 
- Go to [https://www.bitmex.com/app/wallet](https://www.bitmex.com/app/wallet) and click the 'save as CSV' on the top right.  - This will download 'Wallet History - YYYY-MM-DD.csv' file. Put this file in the same location as the python script.  
  
## Use via setting up api credentials for your bitmex account
You can save you api credentials to config.json if you want.   
Warning, saving api details in an unencrypted format to a file could be a security risk.  
You don't have to, there is a prompt for the details if you dont have config.json file setup.  

```bash
# Setup your api credentials in config.json 
# api credentials can be generated here:  https://www.bitmex.com/app/apiKeys
cp config.sample.json config.json  
  
# Use the script with the --use-api flag
python bitmex-wallet-parser.py --use-api 
```  
   

# Run some commands 
Script will output a chart for each time you run it. Share and enjoy ! 

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


### Arguments

| Argument | Description |
| -------- | ----------- |
| `-s` | start date, eg '2019-01-01 00:00' |
| `-e` | end date, eg '2019-02-01 00:00' |
| `--show-wallet` | show full wallet balance history including deposit/withdrawals |
| `--show-affiliate` | show affiliate income |
| `--hide-trading` | hide trading data |
| `--showmoney` | add money values to the axis |
| `--use-api` | get bitmex historical data via api |  
  
      
# TODO 
cache/save/check cache/refresh latest data for trading history / candles   

