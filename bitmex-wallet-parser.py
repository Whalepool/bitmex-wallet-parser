#!/usr/bin/env python3.6

# Logging module
import logging
logging.basicConfig(level=logging.INFO)

# Finding files
import glob

# Exit
from sys import exit 

# Datetime 
from datetime import datetime,  timedelta as datetime_timedelta

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
parser.add_argument('--hide-wallet', action='store_true', help='hide wallet / transaction date')
parser.add_argument('--hide-affiliate', action='store_true', help='hide affiliate data')
parser.add_argument('--hide-trading', action='store_true', help='hide trading data')
parser.add_argument('--private', action='store_true', help='hide numerical values')
args = parser.parse_args()

total_plots = 3

if args.hide_wallet    == True:
	total_plots -= 1
if args.hide_affiliate == True:
	total_plots -= 1
if args.hide_trading   == True:
	total_plots -= 1

if total_plots == 0:
	logging.warning('All available plots set to hidden. nothing to show')
	exit()


############################################################


# Get the downloaded bitmex wallet files
files = sorted(glob.glob('Wallet*'))

if len(files) == 0:
	logging.warning('No valid bitmex wallet files found.')
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

# Commented out because now using infer_datetime_format=True at the read_csv level 
# transactiontime to datetime
# UK
# df['transactTime'] = pd.to_datetime( df['transactTime'], format='%d/%m/%Y, %H:%M:%S' )
# US users
# df['transactTime'] = pd.to_datetime( df['transactTime'], format='%d/%m/%Y, %I:%M:%S %p' )

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

start_datetime = pd.to_datetime(df.index.values[0]).to_pydatetime() 
end_datetime   = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) 

candles_json   = finex.api_request_candles( '1D', start_datetime )
last_returned_from_api  = datetime.utcfromtimestamp(candles_json[len(candles_json)-1][0]/1000.0)


while last_returned_from_api < end_datetime:

	# New api start date = the last returned date + 1 period 
	new_api_start_date = last_returned_from_api+datetime_timedelta(seconds=86400)

	# Fetch from the api
	candles_json += finex.api_request_candles( '1D', new_api_start_date )
	last_returned_from_api  = datetime.utcfromtimestamp(candles_json[len(candles_json)-1][0]/1000.0)


# Format into a nice df 
candle_df = pd.read_json(json_dumps(candles_json))
candle_df.rename(columns={0:'date', 1:'open', 2:'close', 3:'high', 4:'low', 5:'volume'}, inplace=True)
candle_df['date'] = pd.to_datetime( candle_df['date'], unit='ms' )
candle_df.set_index(candle_df['date'], inplace=True)
candle_df.sort_index(inplace=True)
del candle_df['date']



############################################################



# Begin plot
fig = plt.figure(facecolor='white', figsize=(12, 8), dpi=100)
fig.suptitle('Bitmex Account History & Performance')

on_plot = 1

"""
Wallet / Transaction History
"""
if args.hide_wallet != True:

	ax1 = plt.subplot(total_plots,1,on_plot)
	on_plot += 1

	ax1.set_title('Transaction History')

	# If flagged private, hide btc values
	if args.private == True:
		ax1.get_yaxis().set_ticks([])
	else:
		ax1.set_ylabel('BTC')

	ax1.plot( df.index.values, df['amount'].values.cumsum()/100000000, color='b') 
	ax1.fmt_xdata = mdates.DateFormatter('%d/%m/%Y')


	# Add bitcoin price 
	ax11 = ax1.twinx()
	ax11.set_yscale('log')
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
if args.hide_affiliate != True:

	ax2 = plt.subplot(total_plots,1,on_plot)
	on_plot += 1
	
	ax2.set_title('Affiliate income')

	# If flagged private, hide btc values
	if args.private == True:
		ax2.get_yaxis().set_ticks([])
	else:
		ax2.set_ylabel('BTC')

	mask = (df['transactType'] == 'AffiliatePayout')
	ax2.plot( df[mask].index.values, df[mask]['amount'].values.cumsum()/100000000, color='b') 
	ax2.fmt_xdata = mdates.DateFormatter('%d/%m/%Y')


	# Add bitcoin price 
	ax22 = ax2.twinx()
	ax22.set_yscale('log')
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
	if args.private == True:
		ax3.get_yaxis().set_ticks([])
	else:
		ax3.set_ylabel('BTC')

	mask = (df['transactType'] == 'RealisedPNL')
	ax3.plot( df[mask].index.values, df[mask]['amount'].values.cumsum()/100000000, color='b') 
	ax3.fmt_xdata = mdates.DateFormatter('%d/%m/%Y')


	# Add bitcoin price 
	ax33 = ax3.twinx()
	ax33.set_yscale('log')
	ax33.fill_between(candle_df.index.values, candle_df['low'].min(), candle_df['close'].values, facecolor='blue', alpha=0.2)
	ax33.yaxis.set_major_formatter(ScalarFormatter())



############################################################



# Format dates
fig.autofmt_xdate()

# Save figure 
saved_plot_filename = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')+'.png'
plt.savefig(saved_plot_filename, bbox_inches='tight')



############################################################



pprint(wallet_file)
pprint(df.head(4))
