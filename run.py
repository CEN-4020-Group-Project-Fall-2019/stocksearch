#!/usr/bin/env python2
from alpha_vantage.timeseries import TimeSeries as av
import threading
import csv
import time
import urllib2
import os
import sys
import json
import grequests as requests
import pickle
import pandas
import io
from datetime import datetime
import resource

resource.setrlimit(resource.RLIMIT_NOFILE, (110000, 110000))

executable_path = "/home/aidan/stocks/"
exchange_path = "/home/aidan/stocks/exchanges/"
stock_path = "/home/aidan/stocks/data/"
proc_path = "/home/aidan/stocks/proc/"
optionPath = "/home/aidan/stocks/options/"
block = 32768
optionURL = "https://query1.finance.yahoo.com/v7/finance/options/"

# TODO: switch from alphavantage to using yahoo's query1 historical data from beginning of time to present, need to get individual crumb code to download historical data
# requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
class Stock(threading.Thread):
	def __init__(self, symbol):
		super(Stock, self).__init__()
		self.success = False
		self.symbol = symbol
		self.session = requests.Session()
		# self.ts = av(key='PRP85LL7AYYVHTZD', output_format='csv')
		# self.ts = av(key='AJ3OQA9ZGO0LM923', output_format='csv')
		
		
					# self.success = False
			# else:
				# self.success = False
			# print data.text
			# substr[substr[substr.find(':'):].find(':')+1
			# print self.session.files
			# help(self.session)
			# 2018-11-02,1073.729980,1082.974976,1054.609985,1057.790039,1057.790039,1838200
			

			# 2018-11-02,1073.7300,1082.9700,1054.6100,1057.7900,1839043

			
			
			
			

	def run(self):
		# TODO: Issue with threads not starting until after all threads have been initted/started
		
		# self.data, self.meta = self.ts.get_daily(symbol=self.symbol, outputsize='full')#, interval='1min')
		crumbFile =  self.session.get("https://finance.yahoo.com/quote/"+self.symbol+"?p="+self.symbol)
		if crumbFile.ok:
			print "Got to start"
			if "CrumbStore" in crumbFile.text:
				substr = crumbFile.text[crumbFile.text.find("\"CrumbStore"):crumbFile.text[crumbFile.text.find("CrumbStore"):].find(',')+crumbFile.text.find("CrumbStore")]
				substr = '{' + substr + '}'
				j = json.loads(substr)
				# print j["CrumbStore"]["crumb"]
				self.data = self.session.get("https://query1.finance.yahoo.com/v7/finance/download/"+self.symbol+"?period1=0000000000&period2=" + str(int(time.time())) + "&interval=1d&events=history&crumb="+j["CrumbStore"]["crumb"])
				options = self.session.get(optionURL + self.symbol)
				if options.ok:
					self.optionData = options.text
					self.success = True
				else:
					print optionURL + self.symbol + " URL Not Found"

		if self.success:
			print "Starting " + self.symbol
			with open(optionPath + self.symbol + '.csv', 'w') as optionFile:
				# optionFile.write(buf)
				# for date in rawOptionData['optionChain']['result'][0]['expirationDates']:
				# 	print date
				procOptionData = json.loads(self.optionData)
				for date in procOptionData['optionChain']['result'][0]['expirationDates']:
					# if not os.path.isfile(optionPath+self.symbol+".csv")
					# print date
					
					curOptionGet = self.session.get(optionURL + self.symbol + "?date=" + str(date))
					if curOptionGet.ok:
						curOptionData = curOptionGet.text
						processed = json.loads(curOptionData)
						# print str(processed['optionChain']['result'][0]['quote']['bid']) + ' ' + str(processed['optionChain']['result'][0]['quote']['ask'])
						# print "###############Puts###############"
						for item in processed['optionChain']['result'][0]['options'][0]['puts']:
							optionFile.write("P" + ',' + str(date) + ',' + str(item['strike']) + "," + str(item['bid']) + "," + str(item['ask']) + "," + str(item["impliedVolatility"])+'\n')

						# print "###############Calls###############"
						for item in processed['optionChain']['result'][0]['options'][0]['calls']:
							optionFile.write("C" + ',' + str(date) + ',' + str(item['strike']) + "," + str(item['bid']) + "," + str(item['ask']) + "," + str(item["impliedVolatility"])+'\n')

					else:
						print optionURL + self.symbol + " URL Not Found" + "?date=" + str(date)
						return

				with open(proc_path + self.symbol + ".csv", 'w') as file:
				# 	reader = csv.DictReader(self.data.text)
				# 	writer = csv.writer(file)
				# 	print "Writing AV Buffer"
				# 	for row in reader:
				# 		writer.writerow(row[])
					readin = pandas.read_csv(io.StringIO(self.data.text), header=0)
					readin.drop(columns=['Adj Close'])
					file.write(readin.to_csv(header=False, index=False))
					# os.system("tail -n +2 " + stock_path + self.symbol + ".csv | tac > " + proc_path + self.symbol + ".csv")
					# os.system("cat "+ stock_path + self.symbol + ".csv | tac > " + proc_path + self.symbol + ".csv")
				os.system(executable_path + "calc " + self.symbol)
			
			
		# print self.symbol
		# print self.meta
		# os.system("python " + executable_path + "plot.py " + proc_path + self.symbol + ".csv ")# + self.symbol)
		
class Exch():
	def __init__(self, exchange):
		self.exchange = exchange
		self.filepath = exchange_path + exchange + ".csv"
		self.url = urllib2.urlopen("https://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange="+self.exchange+"&render=download")
		self.file = open(self.filepath, "w")

		while True:
			buf = self.url.read(block)
			if not buf:
				break
			self.file.write(buf)

		self.file.close()

def main():
	exchanges = []
	exchanges.append(Exch("nasdaq"))
	# exchanges.append(Exch("nyse"))
	# exchanges.append(Exch("amex"))
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
	# symbols = ["AABA"]

	threads = []

	for stock in symbols:
		start = datetime.now()
		print stock
		thread = Stock(stock)
		thread.start()
		threads.append(thread)
		# threads[-1].start()
		# break
		# while(True):
		# 	if((datetime.now() - start).microseconds >= 50000):
		# 		break
		# time.sleep(4) #required to avoid >15 calls per minute to Alpha Vantage

	for thread in threads:
		thread.join()

	# os.system(executable_path + "calc")

if __name__ == '__main__':
	main()