#!/usr/bin/env python3.6

# Logging module
import coloredlogs, logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

# Datetime 
from datetime import datetime,  timedelta as datetime_timedelta
import time
from dateutil.relativedelta import relativedelta

# For api requests
from requests import get as requests_get

# # Loading/unloading json (for api requests)
from json import dumps as json_dumps, loads as json_loads



class Timeperiods:


	timeframes_list = ['1T','5T','15T','30T','1H','2H','3H','4H','6H','8H','12H','1D','W-MON','MS']
	timeframes = {
		'1T'   : {                    
			'seconds': 60, 
		},
		'5T'   : { 
			'upcycle': '1T',   
			'seconds':5*60,
			'group_intervals': [0,5,10,15,20,25,30,35,40,45,50,55]
		}, 
		'15T'  : { 
			'upcycle': '5T',   
			'seconds':15*60,
			'group_intervals': [0,15,30,45]
		}, 
		'30T'  : { 
			'upcycle': '15T',  
			'seconds':30*60,
			'group_intervals': [0,30]
		}, 
		'1H'   : { 
			'upcycle': '30T',  
			'seconds':60*60,
			'group_intervals': [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
		}, 
		'2H'   : { 
			'upcycle': '1H',   
			'seconds':2*(60*60),
			'group_intervals': [0,2,4,6,8,10,12,14,16,18,20,22]
		}, 
		'3H'   : { 
			'upcycle': '1H',   
			'seconds':3*(60*60),
			'group_intervals': [0,3,6,9,12,18,21]
		}, 
		'4H'   : { 
			'upcycle': '2H',   
			'seconds':4*(60*60),
			'group_intervals': [0,4,8,12,16,20]
		}, 
		'6H'   : {
			'upcycle': '3H',   
			'seconds':6*(60*60),
			'group_intervals': [0,6,12,18]
		}, 
		'8H'   : { 
			'upcycle': '4H',   
			'seconds':8*(60*60),
			'group_intervals': [0,8,16] 
		}, 
		'12H'  : { 
			'upcycle': '6H',   
			'seconds':12*(60*60),
			'group_intervals': [0,12]
		}, 
		'1D'   : { 
			'upcycle': '12H',  
			'seconds':24*(60*60) 
		}, 
		'W-MON': { 
			'upcycle': '1D',  
			'seconds':7*(24*(60*60))
		}, 
		'MS'   : { 
			'upcycle': '1D',  
		}
	}

	def __init__(self):
		pass 

	def increment_timeperiods(self, orig_timestamp, num=1, resolution=None):

		if resolution == None:
			resolution = '1T'

		if resolution == 'MS': 
			output =  orig_timestamp + relativedelta(months=num)
			return output
		else:
			output = orig_timestamp + relativedelta(seconds=(self.timeframes[resolution]['seconds']*num))
			return output 


	def now(self):
		return DateUtils.now_utc().replace(second=0, microsecond=0)

	def get_timeperiods(self, now=None, resolution=None):

		periods = {} 

		if now == None:
			now = self.now()

		year   = now.year
		month  = now.month
		day    = now.day
		hour   = now.hour
		minute = now.minute


		periods['1T'] = now

		# 5T, 15T, 30T 
		bins = ['5T','15T','30T']
		for timeperiod in bins: 

			p = str(year)+"-"+str(month).zfill(2)+"-"+str(day).zfill(2)+" "+str(hour).zfill(2)+":00"

			for i in Timeperiods.timeframes[ timeperiod ]['group_intervals']:
				if i <= minute:
					p = str(year)+"-"+str(month).zfill(2)+"-"+str(day).zfill(2)+" "+str(hour).zfill(2)+":"+str(i).zfill(2)
			
			periods[timeperiod] = datetime.strptime(p, '%Y-%m-%d %H:%M')


		# 1H 
		p = str(year)+"-"+str(month).zfill(2)+"-"+str(day).zfill(2)+" "+str(hour).zfill(2)+":00"
		p = datetime.strptime(p, '%Y-%m-%d %H:%M')
		periods['1H'] = p

		# 2H, 3H, 4H, 6H, 8H, 12H
		bins = ['2H','3H','4H','6H','8H','12H']
		for timeperiod in bins: 

			p = str(year)+"-"+str(month).zfill(2)+"-"+str(day).zfill(2)+" 00:00"
			for i in Timeperiods.timeframes[ timeperiod ]['group_intervals']:
				if i <= hour:
					p = str(year)+"-"+str(month).zfill(2)+"-"+str(day).zfill(2)+" "+str(i).zfill(2)+":00"
			
			periods[timeperiod] = datetime.strptime(p, '%Y-%m-%d %H:%M')


		# 1D 
		p = str(year)+"-"+str(month).zfill(2)+"-"+str(day).zfill(2)
		p = datetime.strptime(p, '%Y-%m-%d').replace(hour=0, minute=0)
		periods['1D'] = p

		# W-MON
		to_beggining_of_week = datetime_timedelta(days=now.weekday())
		p = (now - to_beggining_of_week).replace(hour=0, minute=0)
		periods['W-MON'] = p

		# M
		p = datetime.strptime(str(year)+"-"+str(month).zfill(2)+"-01", '%Y-%m-%d')
		#next_month = p.replace(day=28) + datetime_timedelta(days=4)
		#p = next_month - datetime_timedelta(days=next_month.day)
		periods['MS'] = p


		if resolution != None:
			return periods[resolution]

		else:
			return periods



############################################################
class BFX( Timeperiods ):

	api_limit_seconds = 5
	resolution_to_api = { 
		'1T':  '1m',
		'5T':  '5m',
		'15T': '15m',
		'30T': '30m',
		'1H':  '1h',
		'2H':  '1h',
		'3H':  '3h',
		'4H':  '1h',
		'6H':  '6h',
		'12H': '12h',
		'1D':  '1D',
		'2D':  '1D',
		'W-MON':  '1D'
	}
	api_timeframe_resample_mapping = {
		'2H'   : '1H',
		'4H'   : '1H',
		'2D'   : '1D',
		'W-MON': '1D'
	}

	def datetime_to_miliseconds(self, inputdate=None):
		if inputdate == None:
			inputdate = datetime.utcnow()
		return (inputdate - datetime.utcfromtimestamp(0)).total_seconds() * 1000 



	def api_request_candles(self, resolution, ticker, start_date=None, end_date=None, limit=200):


		resolution_api = resolution
		resolution_increment = resolution


		if resolution in self.api_timeframe_resample_mapping: 

			resolution_increment = self.api_timeframe_resample_mapping[ resolution ]

			logger.info('Getting optimal subperiod, '+str(resolution_increment)+' end date.')

			next_timeperiod = self.increment_timeperiods( end_date, 1 )
			optimal_subperiod = self.increment_timeperiods( end_date, 1, resolution_increment )
			while optimal_subperiod < next_timeperiod:
				if optimal_subperiod < self.now():
					end_date = optimal_subperiod

				optimal_subperiod = self.increment_timeperiods( optimal_subperiod, 1, resolution_increment )
	
		if start_date == None:
			start_date = self.get_timeperiods(resolution=resolution)
			start_date = self.increment_timeperiods( start_date, -limit )
			limit = 200

		if end_date == None:
			end_date = self.get_timeperiods(resolution=resolution)

		start_date_ms = self.datetime_to_miliseconds(start_date)
		end_date_ms = self.datetime_to_miliseconds(end_date)

		logger.info( 'Api request candles from '+str(start_date)+' to '+str(end_date) )

		# Base URL to be getting the candlestick data from
		base_url     = 'https://api.bitfinex.com/v2/candles/trade:'+resolution_api+':t'+ticker+'/hist?limit='+str(limit)
		

		if start_date != None:
			api_query_url = base_url+'&start='+str(start_date_ms)+'&sort=1'
		
		candles = self.api_request( api_query_url )
		cut_off = len(candles)

		for i,c in enumerate(candles):

			if c[0] > end_date_ms:
				cut_off = i 
				break

		candles = candles[0:cut_off]

		logger.info( 'First candle returned: '+str( datetime.utcfromtimestamp(candles[0][0]/1000.0) )+', '+str(candles[0]) )
		logger.info( 'Last candle returned: '+str( datetime.utcfromtimestamp(candles[len(candles)-1][0]/1000.0) )+', '+str(candles[len(candles)-1]) )

		last_date_ms = candles[len(candles)-1][0]

		while last_date_ms < end_date_ms:

			api_query_url = base_url+'&start='+str(last_date_ms)+'&sort=1'
			api_candles   = self.api_request( api_query_url )
			cut_off       = len(api_candles)-1

			for i, c in enumerate(api_candles):
				if c[0] > end_date_ms:
					cut_off = i
					break

			candles       = candles[0:len(candles)-1] + api_candles[0:cut_off+1]

			logger.info('First candle returned: '+str( datetime.utcfromtimestamp(api_candles[0][0]/1000.0) )+', '+str(api_candles[0]) )
			logger.info( 'Last candle used: '+str( datetime.utcfromtimestamp(api_candles[cut_off][0]/1000.0) )+', '+str(api_candles[cut_off]) )

			last_date_ms = candles[len(candles)-1][0]


		output = [] 

		candle_len = len(candles)

		for i,candle in enumerate(candles):

			c = self.candles_map_api_to_list( candle ) 
			output.append(c)	

			expected_nxt_ms = int( self.datetime_to_miliseconds( self.increment_timeperiods( c['timestamp'], 1, resolution_increment ) ) )

			if i < candle_len-1:

				if candles[i+1][0] != expected_nxt_ms:

					logger.warning('Api returned missing candles, at '+str(candle[0])+', expected '+str(expected_nxt_ms)+', got '+str(candles[i+1][0]) )
					logger.warning('at: '+str( datetime.utcfromtimestamp(candle[0]/1000.0) ))
					logger.warning('expected_nxt_ms: '+str( datetime.utcfromtimestamp(expected_nxt_ms/1000.0) ))
					logger.warning('got: '+str( datetime.utcfromtimestamp(candles[i+1][0]/1000.0) ))

					done = False
					while done == False:

						fake_candle = [ expected_nxt_ms, candle[2], candle[2], candle[2], candle[2], 0 ]
						logger.warning('Caution: Adding fake candle '+str( datetime.utcfromtimestamp(expected_nxt_ms/1000.0) )+' '+str(fake_candle))
						c = self.candles_map_api_to_list( fake_candle )
						output.append(c)

						expected_nxt_ms = expected_nxt_ms + (self.timeframes[resolution_increment]['seconds']*1000)
						if expected_nxt_ms == candles[i+1][0]:
							done = True 
						elif expected_nxt_ms < candles[i+1][0]:
							continue 
						elif expected_nxt_ms > candles[i+1][0]:
							error('The expected next timestamp: '+str(expected_nxt_ms)+' is greater than the next timestamp: '+str(candles[i+1][0]))
							exit()


		if resolution in self.api_timeframe_resample_mapping: 
			df = self.list_to_df(output).resample(resolution, closed='left', label='left').agg(self.resample_aggregation)

			output = [] 
			for index, row in df.iterrows():
				output.append({ 
					'timestamp': index.to_pydatetime(),
					'open': row['open'],
					'high': row['high'],
					'low': row['low'],
					'close': row['close'],
					'volume': row['volume']
				})

		return output


	def api_request(self, url):

		if (self.api_limit_seconds > 0): 

			logger.info('Slow api mode, sleeping for '+str(self.api_limit_seconds)+' seconds')
			time.sleep(self.api_limit_seconds)

		logger.info( 'Requesting: '+url ) 

		response = requests_get(url).text
		data     = json_loads(response)

		# Check we actually got the data back 
		# Not just an api error 
		completed = 0 
		while completed == 0:

			if isinstance(data, list):

				if str(data[0]) == 'error': 

					# Log the error
					lmsg = 'BFX API Error: '+str(data)
					error(lmsg)

					# give it a bit of time
					time.sleep(15)
					
					# Re-request the data
					response = requests_get(url).text

					# Load the response
					data = json_loads(response)

					## Re-run

				else:
					# The response json does not contain error
					# Therefore we have the response we wanted
					# So api request actuall completed successfully
					completed = 1

			elif isinstance(data, dict):

				if 'error' in data:

					# Log the error
					lmsg = 'BFX API Error: '+str(data)
					error(lmsg)

					# give it a bit of time
					error('Sleeping for '+str(config.bfx_api_rate_limit_delay)+' seconds')
					time.sleep(config.bfx_api_rate_limit_delay)
					
					# Re-request the data
					response = requests_get(url).text

					# Load the response
					data = json_loads(response)


			else:
				# WTF has the api returned then ? 
				lmsg = 'API error'
				error(data)
				error(lmsg)
				exit()		



		return data


	def candles_map_api_to_list(self, row, offset=True):

		ts = row[0]

		return { 
			'timestamp': datetime.utcfromtimestamp(ts/1000.0),
			'open': row[1],
			'high': row[3],
			'low': row[4],
			'close': row[2],
			'volume': row[5]
		}