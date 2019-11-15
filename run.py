#!/usr/bin/env python3
from gevent import monkey
monkey.patch_all()
import threading
import csv
import time
import urllib.request as urllib2
import os
import sys
import json
import grequests as requests
import pickle
import pandas
import numpy
import io
from datetime import datetime
import resource
import xml.etree.ElementTree as ET
import pyrebase as base

config = {
	"apiKey": "AIzaSyD5nvLGP014aCjjP-wNe_uwZo3orlLiG9Q",
	"authDomain": "heimdallcen4020.firebaseapp.com",
	"databaseURL": "https://heimdallcen4020.firebaseio.com",
	"storageBucket": "heimdallcen4020.appspot.com"
}

firebase = base.initialize_app(config)
db = firebase.database()

resource.setrlimit(resource.RLIMIT_NOFILE, (110000, 110000))
executable_path = os.getcwd() 
exchange_path = executable_path + "/exchanges/"
stock_path = executable_path + "/data/"
proc_path = executable_path + "/proc/"
optionPath = executable_path + "/options/"
block = 32768
optionURL = "https://query1.finance.yahoo.com/v7/finance/options/"

class Stock(threading.Thread):
	def __init__(self, symbol):
		super(Stock, self).__init__()
		self.success = False
		self.symbol = symbol
		self.session = requests.Session()

	def run(self):
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
					for item in processed['optionChain']['result'][0]['options'][0]['puts']:	#issue with ootm options not having bid/ask (makes sense)
						db.child("puts").child(self.symbol).child(str(int(float(item["strike"])*100))).child(str(item["expiration"])).set(item)
					for item in processed['optionChain']['result'][0]['options'][0]['calls']:
						db.child("calls").child(self.symbol).child(str(int(float(item["strike"])*100))).child(str(item["expiration"])).set(item)
				else:
					print(optionURL, self.symbol, " URL Not Found", "?date=", str(date))
					return
			# readin = pandas.read_csv(io.StringIO(self.data.text), header=0)
			# readin.drop(columns=['Adj Close'])
			# print(self.data.text)
			# print(json.loads(readin.to_json()))
			db.child("stocks").child(self.symbol).set(json.loads(self.data.text)["chart"]["result"][0])
	
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
		thread = Stock(stock)
		thread.start()
		threads.append(thread)
		if len(threads) == 16:
			for t in threads:
				t.join()
			threads = []

if __name__ == '__main__':
    main()
