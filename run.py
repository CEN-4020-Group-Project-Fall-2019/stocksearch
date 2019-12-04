#!/usr/bin/env python3
from gevent import monkey
monkey.patch_all()
import threading
import csv
import urllib.request as urllib2
import os
import sys
import json
import grequests as requests
import io
from datetime import datetime
import resource
import xml.etree.ElementTree as ET
import pyrebase as base
import copy
import mysql.connector as sql
import numpy

import twitter
import time
import argparse

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types


config = {
	"apiKey": "AIzaSyD5nvLGP014aCjjP-wNe_uwZo3orlLiG9Q",
	"authDomain": "heimdallcen4020.firebaseapp.com",
	"databaseURL": "https://heimdallcen4020.firebaseio.com",
	"storageBucket": "heimdallcen4020.appspot.com"
}

firebase = base.initialize_app(config)
db = firebase.database()
api = twitter.Api(consumer_key= 'Z4HlCdEhEJk8SlLHzsZDx9fxw', consumer_secret='xLM61gbcSy3InKE7QCVfhZHDstYaPBJNdMBTBC9cfl11BgM27X' , access_token_key='977249287-f4r7WLtpa15LaxsXNOsNk7fT8pGc0NHchC5vzPl1', access_token_secret='aAMDaG7OcdqbebajEYSXDcTAbTimlLnV9InRdUpkFqP0U')
# resource.setrlimit(resource.RLIMIT_NOFILE, (110000, 110000))
executable_path = os.getcwd() 
exchange_path = executable_path + "/exchanges/"
stock_path = executable_path + "/data/"
proc_path = executable_path + "/proc/"
optionPath = executable_path + "/options/"
block = 32768
optionURL = "https://query1.finance.yahoo.com/v7/finance/options/"
class Stock(threading.Thread):
	def __init__(self, symbol, tRate):
		super(Stock, self).__init__()
		self.success = False
		self.symbol = symbol
		self.session = requests.Session()
		# self.db = sql.connect(host='database-1.cedqzlba2fep.us-east-1.rds.amazonaws.com', port=3306, user='pi', passwd='password')
		# self.cx = self.db.cursor()
		self.R = tRate

	def preProcPriceData(self):
		priceData = self.stockData['indicators']['quote'][0]
		self.processedPriceData = {}
		count = 0
		if 'timestamp' in self.stockData.keys():
			for i in self.stockData['timestamp']:
				if not priceData['close'][count] == None and not priceData['open'] == None and not priceData['volume'] == None:
					self.processedPriceData[i] = {}
					self.processedPriceData[i]['close'] = priceData['close'][count]
					self.processedPriceData[i]['open'] = priceData['open'][count]
					self.processedPriceData[i]['volume'] = priceData['volume'][count]
				count += 1
		self.stockData = None
		
	def getSBSPrices(self, per='close'):
		self.prices = []
		self.times = []
		times = [int(t) for t in list(self.processedPriceData.keys())]
		prices = [float(t[per]) for t in list(self.processedPriceData.values())]
		if times:
			startTime = times[0]
			endTime = times[-1]
			prevPrice = prices[0]
			curIndex = 0
			curTime = startTime
			while curTime < endTime:
				while times[curIndex] < curTime:
					curIndex += 1
				dt = times[curIndex] - times[curIndex-1]
				dp = prices[curIndex] - prices[curIndex-1]
				dpodt = dp/dt
				self.prices.append(prices[curIndex-1] + (curTime-times[curIndex-1]*dpodt))
				self.times.append(curTime)
				curTime += 1
			
	def sma(self, period=15, per="close"):
		integ = []
		for i in range(len(self.prices)-period):
			integ.append(numpy.average(self.prices[i:i+period]))
		return {'p': integ, 't': self.times[period:]}

	def stdev(self, period=15, per="close"):
		var = []
		for i in range(len(self.prices)-period):
			var.append(numpy.std(self.prices[i:i+period]))
		return {'v': var, 't': self.times[period:]}

	def options(self, period=300):
		st = stdev(period=period)
		oPrices = []
		for i in self.calls:
			diff = self.prices[-1]*st['v'][-1]*(i[0]-st['t'][-1])
			pU = self.prices[-1] + diff
			pD = self.prices[-1] - diff
			if pD < 0:
				pd = 0
			mU = pU - i[1]
			mD = pD - i[1]
			mD = min(0, mD)
			mU = min(0, mU)
			valP = (mU-mD)/(pU-pD)
			p = self.prices[-1]*valP + ((mU - (pU*valP))*exp(self.R*(i[0] - st['t'][-1])))
			oPrices.append((i[0], i[1], p))
		return oPrices

	def run(self):
		# client = language.LanguageServiceClient()
		# searchResults = api.GetSearch(term=self.symbol, include_entities=True)
		# scores = [client.analyze_sentiment(document=types.Document(content=s.text, type=enums.Document.Type.PLAIN_TEXT)) for s in searchResults]
		# self.sentiment = numpy.average([s.document_sentiment.score for s in scores])
		# self.magnitude = numpy.average([s.document_sentiment.magnitude for s in scores])
		crumbFile =  self.session.get("https://finance.yahoo.com/quote/"+self.symbol+"?p="+self.symbol)
		if crumbFile.ok:
			print("Downloading ", self.symbol)
			if "CrumbStore" in crumbFile.text:
				substr = crumbFile.text[crumbFile.text.find("\"CrumbStore"):crumbFile.text[crumbFile.text.find("CrumbStore"):].find(',')+crumbFile.text.find("CrumbStore")]
				substr = '{' + substr + '}'
				j = json.loads(substr)
				self.data = self.session.get("https://query1.finance.yahoo.com/v8/finance/chart/"+self.symbol+"?interval=1m&crumb="+j["CrumbStore"]["crumb"])
				options = self.session.get(optionURL + self.symbol)
				if options.ok:
					self.optionData = options.text
					self.success = True
				else:
					print(optionURL, self.symbol, " URL Not Found")
		if self.success:
			print("Starting ", self.symbol)
			procOptionData = json.loads(self.optionData)
			for date in procOptionData['optionChain']['result'][0]['expirationDates']:
				curOptionGet = self.session.get(optionURL + self.symbol + "?date=" + str(date))
				if curOptionGet.ok:
					curOptionData = curOptionGet.text
					processed = json.loads(curOptionData)
					self.puts = []
					self.calls = []
					for item in processed['optionChain']['result'][0]['options'][0]['puts']:
						self.puts.append((item['expiration'], item['strike'], item['lastPrice']))
						# db.child("puts").child(self.symbol).child(str(int(float(item["strike"])*100))).child(str(item["expiration"])).set(item)
					for item in processed['optionChain']['result'][0]['options'][0]['calls']:
						# db.child("calls").child(self.symbol).child(str(int(float(item["strike"])*100))).child(str(item["expiration"])).set(item)
						self.calls.append((item['expiration'], item['strike'], item['lastPrice']))
				else:
					print(optionURL, self.symbol, " URL Not Found", "?date=", str(date))
					return
			self.stockData = json.loads(self.data.text)["chart"]["result"][0]
			# db.child("stocks").child(self.symbol).set(json.loads(self.data.text)["chart"]["result"][0])
			self.preProcPriceData()
			self.isWorthwhile()
			# db.child("stocks").child(self.symbol).child("5s").set(fiveSMA)
			# db.child("stocks").child(self.symbol).child("1m").set(sixtySMA)
	def isWorthwhile(self):
		self.getSBSPrices()
		fiveSMA = self.sma(period=5)
		sixtySMA = self.sma(period=60)
		if len(fiveSMA['p']) and len(sixtySMA['p']):
			if fiveSMA['p'][-1] > sixtySMA['p'][-1]:
				db.child("recommended").child(self.symbol).set({'diff': fiveSMA['p'][-1] - sixtySMA['p'][-1]})
			else:
				db.child("recommended").child(self.symbol).remove()

class Exch():
	def __init__(self, exchange):
		self.exchange = exchange
		self.filepath = exchange_path + exchange + ".csv"
		self.url = urllib2.urlopen("https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange="+self.exchange+"&render=download")
		self.file = open(self.filepath, "wb")

		while True:
			buf = self.url.read(block)
			if not buf:
				break
			self.file.write(buf)
		self.file.close()

def main(): #need to get list of every symbol in nasdaq
	treasurylink = urllib2.urlopen("https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Datasets/yield.xml")
	treasuryrate = 0.0
	with open("treasury.xml", "wb") as file:
		while True:
			buf = treasurylink.read(block)
			if not buf:
				break
			file.write(buf)
		tree = ET.parse("treasury.xml")
		root = tree.getroot()
		treasuryRate = float(root[0][0][1][0][2][0][4].text)
	exchanges = []
	exchanges.append(Exch("nasdaq"))
	symbols = []
	if len(sys.argv) < 2:
		for item in exchanges:
				with open(item.filepath, 'r') as file:
					reader = csv.DictReader(file)
					for row in reader:
						if row['Symbol'] not in symbols and " " not in row['Symbol']:
							symbols.append(row['Symbol'])
	else:
		count = 0
		for item in sys.argv:
			if count > 0:
				symbols.append(item)
			count = count+1

	threads = []
	for stock in symbols:
		start = datetime.now()
		print(stock)
		thread = Stock(stock, treasuryRate)
		thread.start()
		threads.append(thread)
		if len(threads) == 4:
			for t in threads:
				t.join()
			threads = []
			# time.sleep(4)

if __name__ == '__main__':
    main()
