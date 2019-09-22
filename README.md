# stocksearch
Pulls all AMEX stock data from alphavantage, pulls current yahoo option data for each symbol on AMEX, calculates what option prices should be given yearly volatility on CUDA kernels, finds undervalued options. Previous iterations searched for recent TA trends of interest.
Currently under development, excuse the mess.

Requires installation of the following Python3 modules:
plotly
grequests
pickle
pandas
h5py

Requires massive rewrite for CUDA implementation, maybe rewrite for CPU first and then move to CUDA.
