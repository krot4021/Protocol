import requests
import json
import urllib.request
from flask import request
class Markit:
	def __init__(self):
		self.lookup_url = "http://dev.markitondemand.com/Api/v2/Lookup/json"
		self.quote_url = "http://dev.markitondemand.com/Api/v2/Quote/json"

	def company_search(self,string):
		result = self.lookup_url + "?input=" + string
		try:
			r = requests.get(result)
			data = json.loads(r.text)
			return (data)
		except:
			print("Connection Failure!!")
		
		
	def get_quote(self,string):
		result = self.quote_url + "?symbol=" + string
		try:
			r = requests.get(result)
			data = json.loads(r.text)
			return (data)
		except:
			print("Connection Error!!")

# AplhaVantage

class Alpha:
	def av_get_quote(self,string):
		url = "https://www.alphavantage.co/query"
		function = "TIME_SERIES_DAILY"
		symbol = request.form['symbol']
		api_key = "CID6YV65LGYHP9XL"
		data = { "function": function, "symbol": symbol, "apikey": api_key }
		page = requests.get(url, params = data)
		data = page.json()
		return data