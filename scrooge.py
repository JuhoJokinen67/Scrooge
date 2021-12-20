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
		
		if date >= (previousTime + 24*60*60*1000):
			prices[date] = price
			volumes[date] = volume
			previousTime = date
	
	return prices,volumes

def getDataFromAPI(startDate, endDate):
	url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=eur&from={0}&to={1}".format(startDate, endDate)
	r = requests.get(url)
	
	if(r.status_code != 200):
		print("Using API was unsuccessful :(")
		exit(0)
	
	data = r.json()
	
	return separateData(data)
	
def getSecsSinceEpoch(startDate, endDate):
	if "-" in startDate and "-" in endDate:
		startSecs = datetime.strptime(startDate, '%Y-%m-%d').timestamp()
		endSecs = datetime.strptime(endDate, '%Y-%m-%d').timestamp()
	else:
		print("Date in a format not recognized :/")
		exit(0)
		
	startMSecs = int(startSecs)
	endMSecs = int(endSecs) + 60*60
	return startMSecs, endMSecs
	
def longestBearishTrend(prices):
	longest = 0
	currentLongest = 0
	
	pricesListed = list(prices.values())
	for i in range(len(pricesListed)):
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
	
	date,vol = highestVolumeDay(volumes)

	print("Longest bearish trend is", longestBearishTrend(prices))		
	
	print("The day with the highest volume is", msecsToString(date), "and its volume was", vol)
	
	buyDate,sellDate = bestDayToBuy(prices)
	if buyDate == 0 and sellDate == 0:
		print("Buying not recommended within this time frame")
	else:
		print("Buy on", msecsToString(buyDate), "sell on", msecsToString(sellDate))
		
		
main()