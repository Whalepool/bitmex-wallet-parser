#!/usr/bin/env python3.6

# logger module
import matplotlib
import pandas as pd
from sys import exit
import openapi_client as deribit
import csv
from bfx import BFX
from json import dumps as json_dumps, loads as json_loads
from matplotlib.ticker import ScalarFormatter
import matplotlib.patches as mpatches
from matplotlib.patches import Circle
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import dateutil.parser
from datetime import datetime,  timedelta as datetime_timedelta
import glob
import coloredlogs
import logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

# Finding files

# Exit

# Datetime


# dataframe

# Matplotlib for charts
#matplotlib.use('Agg')

# # Loading/unloading json (for api requests)

# Import basic bfx library

# deribit
# https://github.com/deribit/deribit-api-clients/tree/master/python


wallet_file = "Wallet_deribit_all.csv"
MAX_COUNT = 1000

#subbaccount
KEY = ""
SECRET = ""

SHOW_MONEY = False

# keep
start_datetime = None
end_datetime = None
total_plots = 1


def createWalletDeribit():
    # Setup configuration instance
    conf = deribit.configuration.Configuration()
    # Setup unauthenticated client
    client = deribit.api_client.ApiClient(conf)
    publicApi = deribit.PublicApi(client)
    # Authenticate with API credentials
    response = publicApi.public_auth_get(
        'client_credentials', '', '', KEY, SECRET, '', '', '', scope='session:test wallet:read')
    access_token = response['result']['access_token']

    conf_authed = deribit.configuration.Configuration()
    conf_authed.access_token = access_token
    # Use retrieved authentication token to setup private endpoint client
    client_authed = deribit.api_client.ApiClient(conf_authed)
    privateApi = deribit.PrivateApi(client_authed)

    response = privateApi.private_get_settlement_history_by_currency_get(
        "BTC", count=MAX_COUNT)
    data = response['result']
    fieldnames = [
	    	'transactTime',
	    	'amount',
            'transactType',
            'transactStatus'
    ]
    with open(wallet_file, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow({
			'transactTime': 'transactTime',
			'amount': 'amount',
            'transactType': 'transactType',
            'transactStatus': 'transactStatus'
		})
        for x in data['settlements']:
            t = {}
            t['transactTime'], t['amount'], t['transactType'], t['transactStatus'] = datetime.fromtimestamp(x['timestamp']/1000), x['profit_loss'], 'RealisedPNL', 'DONE'
            #print(t)
            writer.writerow(t)


createWalletDeribit()

# Get the list of availabble bitmex wallet files
files = sorted(glob.glob('Wallet*'))

if len(files) == 0:
	logger.critical('No valid deribit wallet files found.')
	exit()

# Get the latest most up to date wallet file
wallet_file = files[len(files)-1]

############################################################

# Parse wallet file to dataframe
df = pd.read_csv(wallet_file, infer_datetime_format=True)

# Remove cancelled transactions
# Remnove current unrealised P&L
mask = (df['transactStatus'] != 'Canceled') & (
    df['transactType'] != 'UnrealisedPNL')
df = df[mask]

# transactiontime to datetime
# df['transactTime'] = df['transactTime'].apply(dateutil.parser.parse)
df['transactTime'] = pd.to_datetime(df['transactTime'], dayfirst=True)


# Set it to be the index
df.set_index(df['transactTime'], inplace=True)

# Sort the df by that index
df.sort_index(inplace=True)

# Convert dates to num for matplotlib
df['mpldate'] = df['transactTime'].map(mdates.date2num)

# Delete the old transactTime column
del df['transactTime']

df = df[start_datetime:end_datetime]


############################################################


"""
Get some bitcoin price data
"""
finex = BFX()

if start_datetime == None:
	start_datetime = pd.to_datetime(df.index.values[0]).to_pydatetime()

now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

if (end_datetime == None) or (end_datetime > now):
	end_datetime = now

logger.info('Querying candles between: ' +
            str(start_datetime)+' and '+str(end_datetime))

candles = finex.api_request_candles(
    '1D', 'BTCUSD', start_datetime, end_datetime)


# Format into a nice df
candle_df = pd.DataFrame.from_dict(candles)
candle_df.set_index(candle_df['timestamp'], inplace=True)
candle_df.drop(['timestamp'], axis=1, inplace=True)
candle_df.sort_index(inplace=True)
candle_df = candle_df[~candle_df.index.duplicated(keep='last')]
candle_df = candle_df[start_datetime:end_datetime]


############################################################


# Begin plot
fig = plt.figure(facecolor='white', figsize=(15, 11), dpi=100)
fig.suptitle('Deribit Account History & Performance')

on_plot = 1
if 1 == True:
    ax3 = plt.subplot(total_plots, 1, on_plot)
    on_plot += 1

    ax3.set_title('Trading Returns')

    if SHOW_MONEY:
        ax3.set_ylabel('BTC')
    else:
        ax3.get_yaxis().set_ticks([])

    mask = (df['transactType'] == ('RealisedPNL' or 'CashRebalance'))
    line = ax3.plot(df[mask].index.values, df[mask]['amount'].values.cumsum(), color='red', label='Performance')
    ax3.fmt_xdata = mdates.DateFormatter('%d/%m/%Y')
    
    ax3.get_xaxis().set_visible(True)

    start = df[mask].index[0]
    candle_df = candle_df[start:]

    # Add bitcoin price
    ax33 = ax3.twinx()
    # ax33.set_yscale('log')
    area = ax33.fill_between(candle_df.index.values, candle_df['low'].min(), candle_df['close'].values, facecolor='blue', alpha=0.2, label='BTCUSD Price')
    ax33.yaxis.set_major_formatter(ScalarFormatter())
    
    red_patch = mpatches.Patch(color='red', label='Trading Returns')
    blue_patch = mpatches.Patch(color='blue', label='BTCUSD Price')
    ax3.legend(handles=[red_patch, blue_patch])

############################################################



# Format dates
fig.autofmt_xdate()

# Save figure 
saved_plot_filename = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')+'.png'
plt.savefig(saved_plot_filename, bbox_inches='tight')



############################################################


print('\033[95m',"-------------------------------", '\033[0m')
print('\033[92m','Using Wallet : '+wallet_file,'\033[0m')
print('\033[95m', "-------------------------------", '\033[0m')
print('\033[93m', 'Candle df contents', '\033[0m')
print(candle_df.head(4))
print(candle_df.tail(4))
print('\033[95m', "-------------------------------", '\033[0m')
print('\033[93m', 'Wallet df contents', '\033[0m')
print(df.head(4))
print(df.tail(4))
print('\033[95m', "-------------------------------", '\033[0m')
print('\033[96m','Saved chart to: '+saved_plot_filename+'\n', '\033[0m')