import sys
import json
from collections import OrderedDict
import time

import urllib
import requests
from bs4 import BeautifulSoup
from PyDictionary import PyDictionary




def getTrademarks(search_phrase):
	# First need to get new state
	mainurl = 'http://tmsearch.uspto.gov/bin/gate.exe?f=login&p_lang=english&p_d=trmk'
	r = requests.get(mainurl)
	search_state = r.url.split('state=')[1]



	search_phrase = '"' + search_phrase + '"'
	search_phrase = urllib.quote_plus(search_phrase)
	url = "http://tmsearch.uspto.gov/bin/gate.exe?state=%(state)s&f=toc&a_search=Submit+Query&p_s_ALL=%(phrase)s&p_L=1000"
	url =  url % {'phrase':search_phrase,'state':search_state}
	r = requests.get(url)
	if "No TESS records were found to match the criteria of your query" in r.text:
		return []

	while len(r.text) < 500:
		r = requests.get(url)

	soup = BeautifulSoup(r.text, 'html.parser')

	tds = ['Word Mark','Goods and Services','Mark Drawing Code','Registration Date','Owner','Disclaimer','Type of Mark','Register','Filing Date','Attorney of Record','Abandonment Date','Distinctiveness Limitation Statement']	
	try:
		rows = soup.find("table", border=2).find_all("tr")
		trademarks = []
		for row in rows:
			data = OrderedDict()
			foo = row.text.split('\n')
			data['Word Mark'] = foo[4]
			data['url'] = 'http://tmsearch.uspto.gov' + row.find('a', href=True)['href']
			try:
				data['serial'] = int(foo[2])
			except:
				data['serial'] = -1
			try:
				data['reg'] = int(foo[3])
			except:
				data['reg'] = -1
			data['LIVE'] = foo[7] == 'LIVE'

			r2 = requests.get(data['url'])
			while len(r2.text) < 500:
				r2 = requests.get(data['url'])

			soup2 = BeautifulSoup(r2.text,'html.parser')
			rows2 = soup2.find_all("td")

			for i in range(len(rows2)):
				for td in tds:
					if rows2[i].text.strip() == td:
						 data[td] = rows2[i+1].text.strip()





			trademarks.append(data)
	except:
		data = {}
		soup2 = BeautifulSoup(r.text,'html.parser')
		rows2 = soup2.find_all("td")

		for i in range(len(rows2)):
			for td in tds:
				if rows2[i].text.strip() == td:
					 data[td] = rows2[i+1].text.strip()





		trademarks = [data]	

	return trademarks



print json.dumps(getTrademarks(sys.argv[1]),indent=4)

def generateSimilar(phrase):
	dictionary=PyDictionary()
	words = phrase.split()
	newwords = {}
	for i in range(len(words)):
		if i not in newwords:
			newwords[i] = []
		for word in dictionary.synonym(words[i]):
			newwords[i].append(word)
	print newwords



generateSimilar(sys.argv[1])
