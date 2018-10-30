from alpha_vantage.timeseries import TimeSeries as av
import threading
import urllib2
import csv
import time
import os
import sys
import json

executable_path = "/home/aidan/stocks/"
exchange_path = "/home/aidan/stocks/exchanges/"
stock_path = "/home/aidan/stocks/data/"
proc_path = "/home/aidan/stocks/proc/"
optionPath = "/home/aidan/stocks/options/"
block = 32768
optionURL = "https://query1.finance.yahoo.com/v7/finance/options/"

# TODO: switch from alphavantage to using yahoo's query1 historical data from beginning of time to present, need to get individual crumb code to download historical data

class Stock(threading.Thread):
	def __init__(self, symbol):
		super(Stock, self).__init__()
		self.symbol = symbol
		# self.ts = av(key='EZR9O8KQ47UHIL9G', output_format='csv')
		self.ts = av(key='AJ3OQA9ZGO0LM923', output_format='csv')
		
		self.success = True
		try:
			self.optionData = urllib2.urlopen(optionURL + self.symbol)
		except urllib2.HTTPError:
			print optionURL + self.symbol + " URL Not Found"
			self.success = False

	def run(self):
		self.data, self.meta = self.ts.get_daily(symbol=self.symbol, outputsize='full')#, interval='1min')
		if self.success:
			with open(optionPath + self.symbol + '.csv', 'w') as optionFile:
				rawOptionData = ""
				while True:
					buf = self.optionData.read(block)
					if not buf:
						break
					rawOptionData += buf
					# optionFile.write(buf)
				# for date in rawOptionData['optionChain']['result'][0]['expirationDates']:
				# 	print date
				procOptionData = json.loads(rawOptionData)
				for date in procOptionData['optionChain']['result'][0]['expirationDates']:
					# if not os.path.isfile(optionPath+self.symbol+".csv")
					optionData = ""
					# print date
					try:
						curOption = urllib2.urlopen(optionURL + self.symbol + "?date=" + str(date))
						while True:
							buf = curOption.read(block)
							if not buf:
								break
							optionData += buf
						processed = json.loads(optionData)
						# print str(processed['optionChain']['result'][0]['quote']['bid']) + ' ' + str(processed['optionChain']['result'][0]['quote']['ask'])
						# print "###############Puts###############"
						for item in processed['optionChain']['result'][0]['options'][0]['puts']:
							optionFile.write("P" + ',' + str(date) + ',' + str(item['strike']) + "," + str(item['bid']) + "," + str(item['ask']) + "," + str(item["impliedVolatility"])+'\n')

						# print "###############Calls###############"
						for item in processed['optionChain']['result'][0]['options'][0]['calls']:
							optionFile.write("C" + ',' + str(date) + ',' + str(item['strike']) + "," + str(item['bid']) + "," + str(item['ask']) + "," + str(item["impliedVolatility"])+'\n')

					except urllib2.HTTPError:
						print optionURL + self.symbol + " URL Not Found" + "?date=" + str(date)
						return
				with open(stock_path + self.symbol + ".csv", 'w') as file:
					writer = csv.writer(file)
					print "Writing AV Buffer"
					for row in self.data:
						writer.writerow(row)
					os.system("tail -n +2 " + stock_path + self.symbol + ".csv | tac > " + proc_path + self.symbol + ".csv")
			
			
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
	# exchanges.append(Exch("nasdaq"))
	# # exchanges.append(Exch("nyse"))
	# # exchanges.append(Exch("amex"))
	# symbols = []
	# for item in exchanges:
	# 		with open(item.filepath, 'r') as file:
	# 			reader = csv.DictReader(file)
	# 			for row in reader:
	# 				if row['Symbol'] not in symbols and " " not in row['Symbol']:
	# 					symbols.append(row['Symbol'])
	symbols = ["AABA"]

	threads = []

	for stock in symbols:
		# start = time.time()
		print stock
		threads.append(Stock(stock))
		threads[-1].start()
		# break
		# while(True):
		# 	if(time.time() - start >= 4):
		# 		break
		# time.sleep(4) #required to avoid >15 calls per minute to Alpha Vantage

	for thread in threads:
		thread.join()

	os.system(executable_path + "calc")

if __name__ == '__main__':
	main()