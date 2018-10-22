import plotly.offline as plot
import plotly.graph_objs as graph
import csv
import os
import sys

n = []
close = []
average = []
shares = []
balance = []
std = []
doubleAve = []
five2 = []
ten2 = []

os.system("time ./calc " + sys.argv[1])

with open('output.csv', 'rb') as file:
	reader = csv.DictReader(file)
	for row in reader:
		n.append(row["n"])
		close.append(row["close"])
		average.append(row["average"])
		shares.append(row["shares"])
		balance.append(row["balance"])
		std.append(row["stdDev"])
		doubleAve.append(row["ten"])
		five2.append(row['five2'])
		ten2.append(row['ten2'])

prices = graph.Scatter(x=n, y=close, mode='lines+markers', name="Price")
averages = graph.Scatter(x=n, y=average, mode='lines+markers', name="MA")
sharesHeld = graph.Scatter(x=n, y=shares, mode='markers', name="Shares")
currentBalance = graph.Scatter(x=n, y=balance, mode='lines+markers', name="Balance")
stdDev = graph.Scatter(x=n, y=std, mode='lines+markers', name="STD")
doubleMA = graph.Scatter(x=n, y=doubleAve, mode='lines+markers', name="2MA")
fived2 = graph.Scatter(x=n, y=five2, mode='lines+markers', name="5d2")
tend2 = graph.Scatter(x=n, y=ten2, mode='lines+markers', name="10d2")

container = [prices, averages, sharesHeld, currentBalance, stdDev, doubleMA, fived2, tend2]

plot.plot(container, filename = sys.argv[1] + ".html")