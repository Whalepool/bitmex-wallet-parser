#!/usr/bin/env python3.6

# Logging module
import logging
logging.basicConfig(level=logging.INFO)

# Datetime 
from datetime import datetime,  timedelta as datetime_timedelta

# For api requests
from requests import get as requests_get

# # Loading/unloading json (for api requests)
from json import dumps as json_dumps, loads as json_loads

############################################################
class BFX(object):

	def datetime_to_miliseconds(self, inputdate):
		epoch = datetime.utcfromtimestamp(0)
		return (inputdate - epoch).total_seconds() * 1000 

	def api_request_candles(self, resolution, start_datetime=None, end_datetime=None, mongodb_format=False):

		"""
		FETCH CANDLESTICK DATA FROM THE BITFINEX API
		resolution, str: Available values: '1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h', '1D', '7D', '14D', '1M' 
		"""

		# Match the pandas timeframe request to the api specific request
		# eg: '1T' = '1m'
		# eg: '1H' = '1h'

		# Base URL to be getting the candlestick data from

		url     = 'https://api.bitfinex.com/v2/candles/trade:'+str(resolution)+':tBTCUSD/hist?limit=200'
		
		if start_datetime != None:

			start_datetime_miliseconds = self.datetime_to_miliseconds(start_datetime)
			url += '&start='+str(start_datetime_miliseconds)+'&sort=1'

		if end_datetime != None:

			end_datetime_miliseconds = self.datetime_to_miliseconds(end_datetime)
			url += '&end='+str(end_datetime_miliseconds)



		# Reqeust the data
		logging.info('Requesting BFX API: url: '+url)

		# Fetch the data from the api 
		response = requests_get(url).text
		candles_json = json_loads(response)


		# Check we actually got the data back 
		# Not just an api error 
		completed = 0 
		while completed == 0:

			# Candle json contains an error
			# So no candle data
			if isinstance(candles_json, list):

				if str(candles_json[0]) == 'error': 

					logging.warning('BFX API Error: '+str(candles_json))
					time.sleep(25)
					response = requests_get(url).text
					candles_json = json_loads(response)

				else:
					completed = 1

			else:
				# WTF has the api returned then ? 
				logging.warning('API error')
				pprint(candles_json)
				exit()
				

		return candles_json
