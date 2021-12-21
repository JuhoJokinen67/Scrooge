import requests
from datetime import datetime, time
import json

def msecsToString(msecs):
	return datetime.strftime(datetime.fromtimestamp(msecs//1000), '%Y-%m-%d')
	
def separateData(data): 
	prices = {}
	volumes = {}
	
	previousTime = 0
	for i in range(len(data['prices'])):
		
		date = data['prices'][i][0]
		price = data['prices'][i][1]
		volume = data['total_volumes'][i][1]
		
		if date >= (previousTime + 24*60*60*1000): # Data will always be in either 1-day, 1-hour ot 5-minute intervals
			prices[date] = price                   # and the first data point will be exactly midnight UTC, so this
			volumes[date] = volume                 # should lead to getting only 1 data point each day at exactly midnight
			previousTime = date
	
	return prices,volumes

def getDataFromAPI(startDate, endDate):
	url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=eur&from={0}&to={1}".format(startDate, endDate)
	r = requests.get(url)
	
	if(r.status_code != 200):
		print("Using API was unsuccessful :(")
		exit(0)
	
	data = r.json() # data in format "prices"=[time,price],[time,price]...
					#                "volumes"=[time,volume],[time,volume]...
					# which is kind of annoying, need to split it into maps with separateData
	
	return separateData(data)
	
def getSecsSinceEpoch(startDate, endDate):
	if "-" in startDate and "-" in endDate:
		startSecs = datetime.strptime(startDate, '%Y-%m-%d').timestamp()
		endSecs = datetime.strptime(endDate, '%Y-%m-%d').timestamp()
	else:
		print("Date in a format not recognized :/")
		exit(0)
		
	startSecs = int(startSecs)
	endSecs = int(endSecs) + 60*60 # add an extra hour to end to make sure we get the end date included in the data
	return startSecs, endSecs
	
def longestBearishTrend(prices):
	longest = 0
	currentLongest = 0
	
	pricesListed = list(prices.values())
	for i in range(1, len(pricesListed)):
		if pricesListed[i] < pricesListed[i-1]:
			currentLongest += 1
			longest = max(currentLongest, longest)
		else:
			currentLongest = 0
		
	return longest
	
def highestVolumeDay(volumes):
	highest = 0
	dayOfHighest = 0
	
	for date in volumes:
		vol = volumes[date]
		if vol > highest:
			highest = vol
			dayOfHighest = date
		
	return dayOfHighest,highest
	
	
def bestDayToBuy(prices):
	buyDate = 0
	sellDate = 0
	
	highestDiff = 0
	currentLowest = 1000000000
	currentLowestDate = 0
	
	# can't just look for lowest and highest here and take the difference at the end, 
	# need to check for it every day
	for date in prices: 
		price = prices[date]
		
		if price < currentLowest:
			currentLowest = price
			currentLowestDate = date
			
		dif = price - currentLowest
		
		if dif > highestDiff:
			highestDiff = dif
			buyDate = currentLowestDate
			sellDate = date
	
	return buyDate,sellDate

def main():
	print("Please input dates in format yyyy-mm-dd")
	startDate = input("Enter start date: ")
	endDate = input("Enter end date: ")
	
	seconds1,seconds2 = getSecsSinceEpoch(startDate, endDate)
	
	prices,volumes = getDataFromAPI(seconds1, seconds2)

	bearish = longestBearishTrend(prices)
	date,vol = highestVolumeDay(volumes)
	buyDate,sellDate = bestDayToBuy(prices)
	
	print("Longest bearish trend is", bearish, "days")		
	print("The day with the highest volume is", msecsToString(date), "and its volume was", vol)
	if buyDate == 0 and sellDate == 0:
		print("Buying not recommended within this time frame")
	else:
		print("Buy on", msecsToString(buyDate), "sell on", msecsToString(sellDate), "to maximize profits")
		
main()
