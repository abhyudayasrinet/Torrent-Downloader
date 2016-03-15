import requests
import json
import bs4
import datetime
import os

#list of tv shows to tract and download
TV_SERIES_LIST = [] 

MONTH_DICT = { #dictionary to convert month from text to digits
		"Jan":"01",
		"Feb":"02",
		"Mar":"03",
		"Apr":"04",
		"May":"05",
		"Jun":"06",
		"Jul":"07",
		"Aug":"08",
		"Sep":"09",
		"Oct":"10",
		"Nov":"11",
		"Dec":"12"
	}

def convert_date(date):
	'''
	Convert date format from 20 Jan. 16 to 2016-01-20
	'''
	date = date.replace('.','').split(' ')
	date[1] = MONTH_DICT[date[1]]
	# print(date[2]+"-"+date[1]+"-"+date[0])
	return datetime.date(int(date[2]), int(date[1]), int(date[0]))

def fix_number(number):
	'''
	return number as string with "0" appened if it's less than 10
	eg. "03"
	'''
	if(int(number)<10):
		return "0"+number
	return number

def get_season(season):
	'''
	Convert season text to torrent search format
	eg. Season 1 -> s01
	'''
	season = season.encode('ascii',"ignore")
	number = season[season.find('season')+len("season")+1:]
	return "s"+fix_number(number)

def load_tv_shows():
	'''
	load all tv shows from the text file
	'''
	f = open("series_list.txt","r")
	for line in f.readlines():
		TV_SERIES_LIST.append(line.strip())
	f.close()


if __name__ == '__main__':

	load_tv_shows()
	print("CHECKING FOR SHOWS : ")
	for show in TV_SERIES_LIST:
		print(show)

	for series in TV_SERIES_LIST:

		#send get request to omdb api to get imdb id of tv show
		response = requests.get("http://www.omdbapi.com/?t="+series+"&plot=short&r=json")
		
		#response is received as json
		data = json.loads(response.text.encode('ascii','ignore'))
		
		
		if("imdbID" not in data.keys()):
			print("unable to get imdb id for "+series)
			continue

		#get imdbID
		imdbID = data['imdbID'] 

		#imdb epsiode list url to scrape
		imdbUrl = "http://www.imdb.com/title/"+imdbID+"/episodes"
		response = requests.get(imdbUrl)
		soup = bs4.BeautifulSoup(response.text, "html.parser")

		episodeNumber = 0
		#iterate over all episode airdate divs
		for airdate in soup.find_all("div","airdate"):
			episodeNumber += 1

			#get airdate in proper format
			aired = convert_date(airdate.text.strip())

			#if the airdate is within 3 days of current date then download the torrent
			if(abs(aired - datetime.date.today()).days < 3 and aired < datetime.date.today()):

				#get season number
				seasonTag = soup.find("h3",{"id":"episode_top"})
				seasonNumber = seasonTag.text

				#create search url
				searchQuery = series + " " + get_season(seasonNumber) + "e" + str(episodeNumber)
				print("getting torrent for " + searchQuery)
				torrentSearchUrl = "https://kat.cr/usearch/" + searchQuery + "/?field=seeders&sorder=desc"

				#scrape the url and get magnet link
				response = requests.get(torrentSearchUrl)
				soup = bs4.BeautifulSoup(response.text, "html.parser")
				dataTable = soup.find("table",{"class":"data"})
				topTorrent = dataTable.find("tr",{"class":"odd"})
				magnetLink = topTorrent.find("a",{"title":"Torrent magnet link"})
				os.startfile(str(magnetLink['href']))