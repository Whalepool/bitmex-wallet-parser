#!/usr/bin/env python3.6

# logger module
import coloredlogs, logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

# Finding files
import glob

# Exit
from sys import exit 

# Datetime 
from datetime import datetime,  timedelta as datetime_timedelta
import dateutil.parser


# dataframe
import pandas as pd 

# Pretty output
from pprint import pprint

# Matplotlib for charts
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Circle
import matplotlib.patches as mpatches
from matplotlib.ticker import ScalarFormatter

# # Loading/unloading json (for api requests)
from json import dumps as json_dumps, loads as json_loads

# Import basic bfx library
from bfx import BFX

# Argparser
import argparse


############################################################



# Args  
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--start_datetime', help='Start date', default=None, type=(lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M')) )
parser.add_argument('-e', '--end_datetime', help='End date', default=None, type=(lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M')) )
parser.add_argument('--show-wallet', action='store_true', help='hide wallet / transaction date')
parser.add_argument('--show-affiliate', action='store_true', help='hide affiliate data')
parser.add_argument('--hide-trading', action='store_true', help='hide trading data')
parser.add_argument('--showmoney', action='store_true', help='hide numerical values')
parser.add_argument('--use-api', action='store_true', help='Fetch historical trading data via bitmex api')

args = parser.parse_args()
start_datetime = args.start_datetime
end_datetime   = args.end_datetime

total_plots = 1

if args.show_wallet    == True:
	total_plots += 1
if args.show_affiliate == True:
	total_plots += 1
if args.hide_trading   == True:
	total_plots -= 1

if total_plots == 0:
	logger.warning('All available plots set to hidden. nothing to show')
	exit()


############################################################


if args.use_api == True:
	
	# pip install bitmex - https://github.com/BitMEX/api-connectors/tree/master/official-http/python-swaggerpy
	import bitmex
	import csv
	from pathlib import Path

	bitmex_api_key    = None
	bitmex_api_secret = None 


	confg_file = Path("config.json")
	if confg_file.is_file():
		with open(confg_file, 'r') as file:
			data = file.read()
			obj  =  json_loads(data)

			if 'bitmex_api_key' not in obj:
				logger.critical('config.json missing bitmex_api_key')
				exit()

			elif 'bitmex_api_secret' not in obj:
				logger.critical('config.json missing bitmex_api_secret')
				exit()

			else:
				bitmex_api_key = obj['bitmex_api_key']
				bitmex_api_secret = obj['bitmex_api_secret']


	if (bitmex_api_key == None) or (bitmex_api_secret == None):

		print('\033[95m',"-------------------------------", '\033[0m')
		print('\033[92m','--use-api is set to True \n','\033[0m')
		print('You do not have your bitmex api keys stored in config.json. You can enter them here.')
		print('If you do not have an api key one can be obtained from: https://www.bitmex.com/app/apiKeys \n')
		print('These keys will not be saved to config.json, you must do that manually as saving api keys in plain text is an important security consideration.\n')

		bitmex_api_key    = input("Enter you Bitmex API Key: ")
		bitmex_api_secret = input("Enter you Bitmex API Secret: ")

	wallet_file  = "Wallet-History-from-api.csv"
	client 	     = bitmex.bitmex(test=False, api_key=bitmex_api_key,api_secret=bitmex_api_secret)
	data         = client.User.User_getWalletHistory(count=5000000).result()

	fieldnames = [
	    	'transactTime',
	    	'transactType',
	    	'amount',
	    	'fee',
	    	'address',
	    	'transactStatus',
	    	'walletBalance'
	    ]
	with open(wallet_file, "w", newline='') as f:
	    writer = csv.DictWriter(f, fieldnames=fieldnames)
	    writer.writerow({
			'transactTime'  : 'transactTime',
			'transactType'  : 'transactType',
			'amount' 	    : 'amount',
			'fee'		    : 'fee',
			'address' 	    : 'address',
			'transactStatus': 'transactStatus',
			'walletBalance' : 'walletBalance'
		})
	    for x in data[0]:
	        t = {}
	        for field in fieldnames:
	        	if field == 'transactTime':
	        		t[field] = x[field].strftime('%Y-%m-%d %H:%M:%S.%f')
	        	else:
	        		t[field] = x[field] 

	        logger.info('Writing row: '+str(t))
	        writer.writerow(t)

else : 
	# Get the downloaded bitmex wallet files
	files = sorted(glob.glob('Wallet*'))

	if len(files) == 0:
		logger.warning('No valid bitmex wallet files found.')
		exit()

	# Get the latest most up to date wallet file
	wallet_file = files[len(files)-1]

############################################################

# Parse wallet file to dataframe
df = pd.read_csv(wallet_file, infer_datetime_format=True)

# Remove cancelled transactions
# Remnove current unrealised P&L
mask = (df['transactStatus'] != 'Canceled') & (df['transactType'] != 'UnrealisedPNL')
df = df[mask]

# transactiontime to datetime
df['transactTime'] = df['transactTime'].apply(dateutil.parser.parse)


# Set it to be the index
df.set_index(df['transactTime'], inplace=True)

# Sort the df by that index
df.sort_index(inplace=True)

# Convert dates to num for matplotlib
df['mpldate'] = df['transactTime'].map(mdates.date2num)

# Delete the old transactTime column
del df['transactTime']



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

logger.info('Querying candles between: '+str(start_datetime)+' and '+str(end_datetime))

candles   = finex.api_request_candles( '1D', 'BTCUSD', start_datetime, end_datetime )


# Format into a nice df 
candle_df = pd.DataFrame.from_dict( candles )
candle_df.set_index(candle_df['timestamp'], inplace=True)
candle_df.drop(['timestamp'], axis=1, inplace=True)
candle_df.sort_index(inplace=True)
candle_df = candle_df[~candle_df.index.duplicated(keep='last')]


############################################################



# Begin plot
fig = plt.figure(facecolor='white', figsize=(15, 11), dpi=100)
fig.suptitle('Bitmex Account History & Performance')

on_plot = 1

"""
Wallet / Transaction History
"""
if args.show_wallet == True:

	ax1 = plt.subplot(total_plots,1,on_plot)
	on_plot += 1

	ax1.set_title('Transaction History')

	# If flagged private, hide btc values
	if args.showmoney == True:
		ax1.set_ylabel('BTC')
	else:
		ax1.get_yaxis().set_ticks([])

	ax1.plot( df.index.values, df['amount'].values.cumsum()/100000000, color='b') 
	ax1.fmt_xdata = mdates.DateFormatter('%d/%m/%Y')


	# Add bitcoin price 
	ax11 = ax1.twinx()
	# ax11.set_yscale('log')
	ax11.fill_between(candle_df.index.values, candle_df['low'].min(), candle_df['close'].values, facecolor='blue', alpha=0.2)
	ax11.yaxis.set_major_formatter(ScalarFormatter())


	"""
	Notcable changes to the wallet balance
	- Annotations 
	- ... maybe for later.
	"""
	# std = df['walletBalance'].std(ddof=1)/2
	# mask = abs(df['walletBalance'] - df['walletBalance'].shift(1)) > std 
	# tmpdf = df[mask]

	# for index, row in tmpdf.iterrows():

	# 	y = df.loc[index]['walletBalance']/100000000
	# 	ax1.annotate( s=row['transactType'], xy=(index, y), arrowprops=dict(facecolor='black', shrink=0.05) )



"""
Affiliate Income
"""
if args.show_affiliate == True:

	ax2 = plt.subplot(total_plots,1,on_plot)
	on_plot += 1
	
	ax2.set_title('Affiliate income')

	# If flagged private, hide btc values
	if args.showmoney == True:
		ax2.set_ylabel('BTC')
	else:
		ax2.get_yaxis().set_ticks([])

	mask = (df['transactType'] == 'AffiliatePayout')
	ax2.plot( df[mask].index.values, df[mask]['amount'].values.cumsum()/100000000, color='b') 
	ax2.fmt_xdata = mdates.DateFormatter('%d/%m/%Y')


	# Add bitcoin price 
	ax22 = ax2.twinx()
	# ax22.set_yscale('log')
	ax22.fill_between(candle_df.index.values, candle_df['low'].min(), candle_df['close'].values, facecolor='blue', alpha=0.2)
	ax22.yaxis.set_major_formatter(ScalarFormatter())


"""
Trading Returns
"""
if args.hide_trading != True:

	ax3 = plt.subplot(total_plots,1,on_plot)
	on_plot += 1
		
	ax3.set_title('Trading Returns')

	# If flagged private, hide btc values
	if args.showmoney== True:
		ax3.set_ylabel('BTC')
	else:
		ax3.get_yaxis().set_ticks([])

	mask = (df['transactType'] == ('RealisedPNL' or 'CashRebalance'))
	line = ax3.plot( df[mask].index.values, df[mask]['amount'].values.cumsum()/100000000, color='red', label='Performance') 
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
print('\033[92m',wallet_file,'\033[0m')
print('\033[95m', "-------------------------------", '\033[0m')
print('\033[93m', 'Candle df contents', '\033[0m')
print(candle_df.head(4))
print(candle_df.tail(4))
print('\033[95m', "-------------------------------", '\033[0m')
print('\033[93m', 'Wallet df contents', '\033[0m')
print(df.head(4))
print(df.tail(4))
print('\033[95m', "-------------------------------", '\033[0m')
