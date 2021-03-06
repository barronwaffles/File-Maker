#!/usr/bin/python
# -*- coding: utf-8 -*-

# ===========================================================================
# NEWS CHANNEL GENERATION SCRIPT
# AUTHORS: LARSEN VALLECILLO
# ****************************************************************************
# Copyright (c) 2015-2017 RiiConnect24, and it's (Lead) Developers
# ===========================================================================

import binascii # Used to write to stuff in hex.
import calendar # Used for the timestamps.
import collections # Used to write stuff in dictionaries in order.
import errno # Used to catch errors when creating dirs recursively.
import newsdownload # Used to call the locations downloader.
import os # Used to remove output from DSDecmp.
import pickle # Used to save and load dictionaries.
import requests
import rsa # Used to make the RSA Signature.
import struct # Needed to pack u32s and other integers.
import subprocess # Needed to run DSDecmp, which is for LZ77 Compression.
import sys
import time # Used to get time stuff.
import urllib2 # Used to open URLs.
from config import *
from datetime import timedelta, datetime, date # Used to get time stuff.
reload(sys)
sys.setdefaultencoding('ISO-8859-1')
requests.packages.urllib3.disable_warnings()

"""This will pack the integers."""

def u8(data):
	if data < 0 or data > 255:
		print "[+] Value Pack Failure: %s" % data
		data = 0
	return struct.pack(">B", data)

def u16(data):
	if data < 0 or data > 65535:
		print "[+] Value Pack Failure: %s" % data
		data = 0
	return struct.pack(">H", data)

def u32(data):
	if data < 0 or data > 4294967295:
		print "[+] Value Pack Failure: %s" % data
		data = 0
	return struct.pack(">I", data)

def u32_littleendian(data):
	if data < 0 or data > 4294967295:
		print "[+] Value Pack Failure: %s" % data
		data = 0
	return struct.pack("<I", data)

# http://stackoverflow.com/a/600612/3874884
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def download_source(name, mode, thumb, language_code, countries, data):
	print "News Channel File Generator \nBy Larsen Vallecillo / www.rc24.xyz\n\nMaking news.bin for %s...\n" % name

	make_news = make_news_bin(mode, "wii", data)
	make_news = make_news_bin(mode, "wii_u", data)

	if production:
		"""This will use a webhook to log that the script has been ran."""
		
		data = {"username": "News Bot", "content": "News Data has been updated!", "avatar_url": "https://rc24.xyz/images/logo-small.png", "attachments": [{"fallback": "News Data Update", "color": "#1B691E", "author_name": "RiiConnect24 News Script", "author_icon": "https://rc24.xyz/images/profile_news.png", "text": make_news, "title": "Update!", "fields": [{"title": "Script", "value": "News Channel (" + name + ")", "short": "false"}], "thumb_url": thumb, "footer": "RiiConnect24 Script", "footer_icon": "https://rc24.xyz/images/logo-small.png", "ts": int(time.mktime(datetime.utcnow().timetuple()))}]}

		for url in webhook_urls:
			requests.post(url, json=data, allow_redirects=True)

		for country in countries:
			copy_file(mode, "wii", country, language_code)
			copy_file(mode, "wii_u", country, language_code)

		newsfilename = "news.bin." + str(datetime.utcnow().hour).zfill(2) + "." + mode + "."
		os.remove(newsfilename + "wii")
		os.remove(newsfilename + "wii_u")

"""Copy the temp files to the correct path that the Wii will request from the server."""

def copy_file(mode, system, country, language_code):
	if (force_all == True):
		for hours in range(0, 24):
			newsfilename = "news.bin.%s.%s.%s" % (str(datetime.utcnow().hour).zfill(2), mode, system)
			newsfilename2 = "news.bin.%s" % (str(hours).zfill(2))
			path = "%s/%s/%s/%s/%s" % (file_path, "v3" if system == "wii_u" else "v2", language_code, country, newsfilename2)
			mkdir_p(path)
			subprocess.call(["cp", newsfilename, path])
	else:
		newsfilename = "news.bin.%s.%s.%s" % (str(datetime.utcnow().hour).zfill(2), mode, system)
		newsfilename2 = "news.bin.%s" % (str(datetime.utcnow().hour).zfill(2))
		path = "%s/%s/%s/%s/%s" % (file_path, "v3" if system == "wii_u" else "v2", language_code, country, newsfilename2)
		subprocess.call(["cp", newsfilename, path])

"""Run the functions to make the news."""

def make_news_bin(mode, console, data):
	if mode == "ap_english":
		topics_news = collections.OrderedDict()

		topics_news["National News"] = "national"
		topics_news["International News"] = "world"
		topics_news["Sports"] = "sports"
		topics_news["Arts/Entertainment"] = "entertainment"
		topics_news["Business"] = "business"
		topics_news["Science/Health"] = "science"
		topics_news["Technology"] = "technology"

		languages = [1, 3, 4]

		language_code = 1

		country_code = 49

	elif mode == "ap_spanish":
		topics_news = collections.OrderedDict()

		topics_news["Generales"] = "general"
		topics_news["Financieras"] = "finance"
		topics_news["Deportivas"] = "sports"
		topics_news["Espectáculos"] = "shows"

		languages = [1, 3, 4]

		language_code = 4

		country_code = 49

	elif mode == "reuters_english":
		topics_news = collections.OrderedDict()

		topics_news["World"] = "world"
		topics_news["UK"] = "uk"
		topics_news["Health"] = "health"
		topics_news["Science"] = "science"
		topics_news["Technology"] = "technology"
		topics_news["Oddly Enough"] = "offbeat"
		topics_news["Entertainment"] = "entertainment"
		topics_news["Sports"] = "sports"

		languages = [1, 2, 3, 4, 5, 6]

		language_code = 1

		country_code = 110

	elif mode == "zeit_german":
		topics_news = collections.OrderedDict()

		topics_news["General"] = "general"
		topics_news["Politik"] = "politics"
		topics_news["Wirtschaft"] = "economy"
		topics_news["Gesellschaft"] = "society"
		topics_news["Kultur"] = "culture"
		topics_news["Wissen"] = "knowledge"
		topics_news["Digital"] = "digital"
		topics_news["Sport"] = "sports"

		languages = [1, 2, 3, 4, 5, 6]

		language_code = 2

		country_code = 110

	elif mode == "afp_french":
		topics_news = collections.OrderedDict()

		topics_news["Top News"] = "topnews"
		topics_news["Société"] = "society"
		topics_news["Monde"] = "world"
		topics_news["Politique"] = "politique"

		languages = [1, 2, 3, 4, 5, 6]

		language_code = 3

		country_code = 110

	elif mode == "ansa_italian":
		topics_news = collections.OrderedDict()

		topics_news["Dal mondo"] = "world"
		topics_news["Dall'Italia"] = "italy"
		topics_news["Sport"] = "sports"
		topics_news["Economia"] = "economy"
		topics_news["Cultura"] = "culture"

		languages = [1, 2, 3, 4, 5, 6]

		language_code = 5

		country_code = 110

	elif mode == "anp_dutch":
		topics_news = collections.OrderedDict()

		topics_news["Algemeen"] = "general"
		topics_news["Economie"] = "economy"
		topics_news["Sport"] = "sports"
		topics_news["Tech"] = "technology"
		topics_news["Entertainment"] = "entertainment"
		topics_news["Lifestyle"] = "lifestyle"
		topics_news["Opmerkelijk"] = "noteworthy"

		languages = [1, 2, 3, 4, 5, 6]

		language_code = 6

		country_code = 110

	elif mode == "news24_mainichi_japanese":
		topics_news = collections.OrderedDict()

		topics_news["政治"] = "politics"
		topics_news["経済"] = "economy"
		topics_news["国際"] = "international"
		topics_news["社会"] = "society"
		topics_news["スポーツ"] = "sports"
		topics_news["芸能文化"] = "entertainment"

		languages = [0]

		language_code = 0

		country_code = 1

	global system
	global dictionaries

	system = console

	numbers = 0

	if not os.path.exists("newstime"):
		os.mkdir("newstime")

	for topics in topics_news.values():
		newstime = collections.OrderedDict()

		for keys in data.keys():
			if topics in keys:
				numbers += 1

				newstime[data[keys][3]] = get_timestamp(1) + u32(numbers)

		pickle.dump(newstime, open("newstime/" + "newstime." + str(datetime.now().hour).zfill(2) + "-" + mode + "-" + topics + "-" + system, "w+"))

	dictionaries = []

	locations_data = newsdownload.locations_download(language_code, data)

	header = make_header(country_code, languages, language_code, 0, 0, 30, data)
	wiimenu_articles = make_wiimenu_articles(header, data)
	topics_table = make_topics_table(header, topics_news, data)
	timestamps_table = make_timestamps_table(topics_table, topics_news, mode, data)
	articles_table = make_articles_table(header, locations_data, data)
	source_table = make_source_table(header, articles_table, data)
	locations_table = make_locations_table(header, locations_data)
	pictures_table = make_pictures_table(header, data)
	articles = make_articles(pictures_table, articles_table, data)
	topics = make_topics(topics_table, source_table, 0, topics_news, 0)
	copyright = make_copyright(source_table, language_code, data)
	locations = make_locations(locations_table, locations_data)
	source_pictures = make_source_pictures(source_table, data)
	pictures = make_pictures(pictures_table, data)
	riiconnect24_text = make_riiconnect24_text()

	write = write_dictionary(mode)

	headlines = []

	for article in data.values():
		if article[3].decode("utf-16be") not in headlines:
			headlines.append(article[3].decode("utf-16be") + "\n")

	return "".join(headlines)

"""This is a function used to count offsets."""

def offset_count():
	return u32(12 + sum(len(values) for dictionary in dictionaries for values in dictionary.values() if values))

"""Return a timestamp."""

def get_timestamp(mode):
	if system == "wii": seconds = 946684800
	elif system == "wii_u": seconds = 748075000

	if mode == 1: return u32(((calendar.timegm(datetime.utcnow().timetuple()) - seconds) / 60))
	elif mode == 2: return u32(((calendar.timegm(datetime.utcnow().timetuple()) - seconds) / 60) + 1500)

"""Make the news.bin."""

"""First part of the header."""

def make_header(country_code, languages, language_code, goo_flag, language_select_screen_flag, download_interval, data):
	header = collections.OrderedDict()
	dictionaries.append(header)

	header["updated_timestamp_1"] = get_timestamp(1) # Updated time.
	header["term_timestamp"] = get_timestamp(2) # Timestamp for the term.
	header["country_code"] = u32_littleendian(country_code) # Wii Country Code.
	header["updated_timestamp_2"] = get_timestamp(1) # 3rd timestamp.

	"""List of languages that appear on the language select screen."""

	numbers = 0

	for language in languages:
		numbers += 1

		header[numbers] = u8(language)
		
	"""Fills the rest of the languages as null."""

	while numbers < 16:
		numbers += 1

		header[numbers] = u8(255)

	header["language_code"] = u8(language_code) # Wii language code.
	header["goo_flag"] = u8(goo_flag) # Flag to make the Globe display "Powered by Goo".
	header["language_select_screen_flag"] = u8(language_select_screen_flag) # Flag to bring up the language select screen.
	header["download_interval"] = u8(download_interval) # Interval in minutes to check for new articles to display on the Wii Menu.
	header["message_offset"] = u32(0) # Offset for a message.
	header["topics_number"] = u32(0) # Number of entries for the topics table.
	header["topics_offset"] = u32(0) # Offset for the topics table.
	header["articles_number"] = u32(0) # Number of entries for the articles table.
	header["articles_offset"] = u32(0) # Offset for the articles table.
	header["source_number"] = u32(0) # Number of entries for the source table.
	header["source_offset"] = u32(0) # Offset for the source table.
	header["locations_number"] = u32(0) # Number of entries for the locations.
	header["locations_offset"] = u32(0) # Offset for the locations table.
	header["pictures_number"] = u32(0) # Number of entries for the pictures table.
	header["pictures_offset"] = u32(0) # Offset for the pictures table.
	header["count"] = u16(480) # Count value.
	header["unknown"] = u16(0) # Unknown.
	header["wiimenu_articles_number"] = u32(0) # Number of Wii Menu article entries.
	header["wiimenu_articles_offset"] = u32(0) # Offset for the Wii Menu article table.
	header["wiimenu_articles_offset"] = offset_count() # Offset for the Wii Menu article table.

	numbers = 0

	headlines = []

	for article in data.values():
		if numbers < 11:
			if article[3] not in headlines:
				numbers += 1
				headlines.append(article[3])
				header["headline_%s_size" % numbers] = u32(0) # Size of the headline.
				header["headline_%s_offset" % numbers] = u32(0) # Offset for the headline.

	return header

"""Headlines to display on the Wii Menu."""

def make_wiimenu_articles(header, data):
	wiimenu_articles = collections.OrderedDict()
	dictionaries.append(wiimenu_articles)

	numbers = 0

	headlines = []

	for article in data.values():
		if numbers < 11:
			if article[3] not in headlines:
				numbers += 1
				headlines.append(article[3])
				header["headline_%s_size" % numbers] = u32(len(article[3])) # Size of the headline.
				header["headline_%s_offset" % numbers] = offset_count() # Offset for the headline.
				wiimenu_articles["headline_%s" % numbers] = article[3] # Headline.
				"""For some reason, the News Channel uses this padding to separate news articles."""
				if (int(binascii.hexlify(offset_count()), 16) + 2) % 4 == 0:
					wiimenu_articles["padding_%s" % numbers] = u16(0) # Padding.
				elif (int(binascii.hexlify(offset_count()), 16) + 4) % 4 == 0:
					wiimenu_articles["padding_%s" % numbers] = u32(0) # Padding.

	header["wiimenu_articles_number"] = u32(numbers) # Number of Wii Menu article entries.

	return wiimenu_articles

"""Topics table."""

def make_topics_table(header, topics_news, data):
	topics_table = collections.OrderedDict()
	dictionaries.append(topics_table)
	header["topics_offset"] = offset_count() # Offset for the topics table.
	topics_table["new_topics_offset"] = u32(0) # Offset for the newest topic.
	topics_table["new_topics_article_size"] = u32(0) # Size for the amount of articles to choose for the newest topic.
	topics_table["new_topics_article_offset"] = u32(0) # Offset for the articles to choose for the newest topic.

	numbers = 0

	for topics in topics_news.values():
		numbers += 1
		topics_table["topics_%s_offset" % str(numbers)] = u32(0) # Offset for the topic.
		topics_table["topics_%s_article_number" % str(numbers)] = u32(0) # Number of articles that will be in a certain topic.
		topics_table["topics_%s_article_offset" % str(numbers)] = u32(0) # Offset for the articles to choose for the topic.

	header["topics_number"] = u32(numbers + 1) # Number of entries for the topics table.

	return topics_table

"""Timestamps table."""

def make_timestamps_table(topics_table, topics_news, mode, data):
	timestamps_table = collections.OrderedDict()
	dictionaries.append(timestamps_table)

	times_list = []
	times_files = []

	def timestamps_table_add(topics):
		times = collections.OrderedDict()
		times_files = []

		for numbers in range(0, 24):
			start_time = datetime.today() - timedelta(hours = numbers)
			times_files.append("newstime/" + "newstime." + str(start_time)[11:-13] + "-" + str(mode) + "-" + topics + "-" + system)

		for files in times_files:
			if os.path.exists(files):
				newstime = pickle.load(open(files, "rb"))

				for keys in newstime.keys():
					if keys not in times:
						times[keys] = newstime[keys]

		times_list = []

		for values in times.values():
			times_list.append(values)

		timestamps = ''.join(times_list) # Timestamps.

		return timestamps

	numbers = 0

	for topics in topics_news.values():
		numbers += 1
		timestamps_add = timestamps_table_add(topics)
		if timestamps_add != 0:
			topics_table["topics_%s_article_number" % str(numbers)] = u32(len(timestamps_add) / 8) # Number of articles that will be in a certain topic. Also, I don't like how it divides the thing by 8 but whatever.
			topics_table["topics_%s_article_offset" % str(numbers)] = offset_count() # Offset for the articles to choose for the topic.
			timestamps_table["timestamps_%s" + str(numbers)] = timestamps_add # Timestamps.

	return timestamps_table

"""Articles table."""

def make_articles_table(header, locations_data, data):
	articles_table = collections.OrderedDict()
	dictionaries.append(articles_table)

	pictures_number = 0
	numbers = 0

	header["articles_offset"] = offset_count()

	for keys,article in data.items():
		numbers += 1
		articles_table["article_%s_number" % numbers] = u32(numbers) # Number for the article.
		articles_table["source_%s_number" % numbers] = u32(0) # Number for the source.
		articles_table["location_%s_number" % numbers] = u32(4294967295) # Number for the location.

		for locations in locations_data.keys():
			for article_name in locations_data[locations][1]:
				if keys == article_name:
					articles_table["location_%s_number" % numbers] = u32(locations_data.keys().index(locations)) # Number for the location.

		if article[4] != 0:
			articles_table["term_timestamp_%s" % numbers] = get_timestamp(1) # Timestamp for the term.
			articles_table["picture_%s_number" % numbers] = u32(pictures_number) # Number for the picture.
			pictures_number += 1
		else:
			articles_table["term_timestamp_%s" % numbers] = u32(0) # Timestamp for the term.
			articles_table["picture_%s_number" % numbers] = u32(4294967295) # Number for the picture.

		articles_table["published_time_%s" % numbers] = article[0] # Published time.
		articles_table["updated_time_%s" % numbers] = get_timestamp(1) # Updated time.
		articles_table["headline_%s_size" % numbers] = u32(len(article[3])) # Size of the headline.

		if len(article[3]) == 0:
			print "Headline is 0."
			print article[3].decode("utf-16be")
			sys.exit(1)
		elif len(article[2]) == 0:
			print "Article is 0."
			print article[2].decode("utf-16be")
			sys.exit(1)

		articles_table["headline_%s_offset" % numbers] = u32(0) # Offset for the headline.
		articles_table["article_%s_size" % numbers] = u32(len(article[2])) # Size of the article.
		articles_table["article_%s_offset" % numbers] = u32(0) # Offset for the article.

	header["articles_number"] = u32(numbers) # Number of entries for the articles table.

	return articles_table

"""Source table."""

def make_source_table(header, articles_table, data):
	source_table = collections.OrderedDict()
	dictionaries.append(source_table)
	header["source_offset"] = offset_count() # Offset for the source table.

	source_articles = []
	
	"""These are the picture and position values."""

	sources = {
		"ap": [0, 3],
		"reuters": [0, 4],
		"AFP": [4, 4],
		"ANP": [0, 5],
		"ansa": [6, 6],
		"dpa": [0, 4],
		"ZEIT ONLINE": [0, 4],
		"SID": [0, 4],
		"mainichi": [1, 1],
		"news24": [0, 2],
		"NU.nl": [0, 5],
	}

	numbers = 0

	numbers_article = 0

	for article in data.values():
		if article[9] not in source_articles:
			source_articles.append(article[9])

			source = sources[article[9]]

			source_table["source_picture_%s" % article[9]] = u8(source[0]) # Picture for the source.
			source_table["source_position_%s" % article[9]] = u8(source[1]) # Position for the source.
			source_table["padding_%s" % article[9]] = u16(0) # Padding.

			source_table["pictures_size_%s" % article[9]] = u32(0) # Size of the source picture.
			source_table["pictures_offset_%s" % article[9]] = u32(0) # Offset for the source picture.

			source_table["name_size_%s" % article[9]] = u32(0) # Size of the source name.
			source_table["name_offset_%s" % article[9]] = u32(0) # Offset for the source name.

			source_table["copyright_size_%s" % article[9]] = u32(0) # Size of the copyright.
			source_table["copyright_offset_%s" % article[9]] = u32(0) # Offset for the copyright.

			numbers += 1

	for article in data.values():
		numbers_article += 1

		articles_table["source_%s_number" % numbers_article] = u32(source_articles.index(article[9])) # Number for the source.

	header["source_number"] = u32(numbers) # Number of entries for the source table.

	return source_table

"""Locations data table."""

def make_locations_table(header, locations_data):
	locations_table = collections.OrderedDict()
	dictionaries.append(locations_table)
	header["locations_offset"] = offset_count() # Offset for the locations table.

	locations_number = 0

	for locations_coordinates in locations_data.keys():
		locations_number += 1
		numbers = locations_data.keys().index(locations_coordinates)
		locations_table["location_%s_offset" % numbers] = u32(0) # Offset for the locations.
		locations_table["location_%s_coordinates" % numbers] = locations_data[locations_coordinates][0] # Coordinates of the locations.

	header["locations_number"] = u32(locations_number) # Number of entries for the locations.

	return locations_table

"""Pictures table."""

def make_pictures_table(header, data):
	pictures_table = collections.OrderedDict()
	dictionaries.append(pictures_table)
	header["pictures_offset"] = offset_count() # Offset for the pictures table.

	real_numbers = 0

	numbers = 0

	for article in data.values():
		numbers += 1
		if article[4] != 0:
			if article[5] != 0:
				pictures_table["credits_%s_size" % numbers] = u32(len(article[5])) # Size of the credits.
				pictures_table["credits_%s_offset" % numbers] = u32(0) # Offset for the credits.
			else:
				pictures_table["credits_%s_size" % numbers] = u32(0) # Size of the credits.
				pictures_table["credits_%s_offset" % numbers] = u32(0) # Offset for the credits.

			if article[6] != 0:
				pictures_table["captions_%s_size" % numbers] = u32(len(article[6])) # Size of the captions.
				pictures_table["captions_%s_offset" % numbers] = u32(0) # Offset for the captions.
			else:
				pictures_table["captions_%s_size" % numbers] = u32(0) # Size of the credits.
				pictures_table["captions_%s_offset" % numbers] = u32(0) # Offset for the captions.

			real_numbers += 1
			pictures_table["pictures_%s_size" % numbers] = u32(len(article[4])) # Size of the pictures.
			pictures_table["pictures_%s_offset" % numbers] = u32(0) # Offset for the pictures.

	header["pictures_number"] = u32(real_numbers) # Number of entries for the pictures table.

	return pictures_table

"""Add the articles."""

def make_articles(pictures_table, articles_table, data):
	articles = collections.OrderedDict()
	dictionaries.append(articles)

	numbers = 0

	for article in data.values():
		numbers += 1
		articles_table["headline_%s_offset" % numbers] = offset_count() # Offset for the headline.
		articles["headline_%s_read" % numbers] = article[3] # Read the headline.
		articles["padding_%s_headline" % numbers] = u16(0) # Padding for the headline.
		articles_table["article_%s_offset" % numbers] = offset_count() # Offset for the article.
		articles["article_%s_read" % numbers] = article[2] # Read the article.
		articles["padding_%s_article" % numbers] = u16(0) # Padding for the article.

		if article[6] != 0:
			pictures_table["captions_%s_offset" % numbers] = offset_count() # Offset for the caption.
			articles["captions_%s_read" % numbers] = article[6] # Read the caption.
			articles["padding_%s_captions" % numbers] = u16(0) # Padding for the caption.
		if article[5] != 0:
			pictures_table["credits_%s_offset" % numbers] = offset_count() # Offset for the credits.
			articles["credits_%s_read" % numbers] = article[5] # Read the credits.
			articles["padding_%s_credits" % numbers] = u16(0) # Padding for the credits.

	return articles

"""Add the topics."""

def make_topics(topics_table, source_table, message, topics_news, message_flag):
	topics = collections.OrderedDict()
	dictionaries.append(topics)

	numbers = 0

	for keys in topics_news.keys():
		numbers += 1
		topics_table["topics_%s_offset" % str(numbers)] = offset_count() # Offset for the topics.
		topics["topics_%s_read" % numbers] = keys.decode("utf-8").encode("utf-16be") # Read the topics.
		topics["padding_%s_topics" % numbers] = u16(0) # Padding for the topics.

	if message_flag == 1:
		header["message_offset"] = offset_count() # Offset for a message.
		topics["message"] = message # Message.

	return topics

def make_copyright(source_table, language_code, data):
	copyright = collections.OrderedDict()
	dictionaries.append(copyright)

	source_articles = []
	
	"""Text for the copyright. Some of these I had to make up, because if you don't specify a copyright there will be a line that will be in the way in the news article."""

	sources = {
		"ap": ("Copyright %s The Associated Press. All rights reserved. This material may not be published, broadcast, rewritten or redistributed." % date.today().year).decode("utf-8").encode("utf-16be"),
		"reuters": ("© %s Thomson Reuters. All rights reserved. Republication or redistribution of Thomson Reuters content, including by framing or similar means, is prohibited without the prior written consent of Thomson Reuters. Thomson Reuters and the Kinesis logo are trademarks of Thomson Reuters and its affiliated companies." % date.today().year).decode("utf-8").encode("utf-16be"),
		"AFP": ("All reproduction and representation rights reserved. © %s Agence France-Presse" % date.today().year).decode("utf-8").encode("utf-16be"),
		"AFP_french": ("Tous droits de reproduction et de diffusion réservés. © %s Agence France-Presse" % date.today().year).decode("utf-8").encode("utf-16be"),
		"ANP": ("All reproduction and representation rights reserved. © %s B.V. Algemeen Nederlands Persbureau ANP" % date.today().year).decode("utf-8").encode("utf-16be"),
		"ansa": ("© %s ANSA, Tutti i diritti riservati. Testi, foto, grafica non potranno essere pubblicali, riscritti, commercializzati, distribuiti, videotrasmessi, da parte dagli tanti e del terzi in genere, in alcun modo e sotto qualsiasi forma." % date.today().year).decode("utf-8").encode("utf-16be"),
		"SID": ("Alle Rechte für die Wiedergabe, Verwertung und Darstellung reserviert. © %s SID" % date.today().year).decode("utf-8").encode("utf-16be"),
		"ZEIT ONLINE": ("© %s ZEIT ONLINE" % date.today().year).decode("utf-8").encode("utf-16be"),
		"dpa": ("© %s dpa" % date.today().year).decode("utf-8").encode("utf-16be"),
		"mainichi": "©毎日新聞社　見出し・記事・写真の無断転載を禁止します。".decode("utf-8").encode("utf-16be"),
		"news24": "Copyright(C)NIPPON TELEVISION NETWORK CORPORATION All rights reserved. 映像協力 NNN(Nippon News Network)".decode("utf-8").encode("utf-16be"),
		"NU.nl": ("© %s Sanoma Digital The Netherlands B.V. NU - onderdeel van Sanoma Media Netherlands Group" % date.today().year).decode("utf-8").encode("utf-16be"),
	}

	for article in data.values():
		if article[9] not in source_articles:
			if article[9] == "AFP":
				if language_code == 3:
					source = sources["AFP_french"]
				else:
					source = sources[article[9]]
			else:
				source = sources[article[9]]

			source_articles.append(article[9])

			source_table["copyright_size_%s" % article[9]] = u32(len(source)) # Size of the copyright.

			if source != "":
				source_table["copyright_offset_%s" % article[9]] = offset_count() # Offset for the copyright.

			copyright["copyright_read_%s" % article[9]] = source # Read the copyright.
			copyright["padding_copyright_%s" % article[9]] = u16(0) # Padding for the copyright.

"""Add the locations."""

def make_locations(locations_table, locations_data):
	locations = collections.OrderedDict()
	dictionaries.append(locations)

	for locations_strings in locations_data.keys():
		numbers = locations_data.keys().index(locations_strings)
		locations_table["location_%s_offset" % numbers] = offset_count() # Offset for the locations.

		locations["location_%s_read" % numbers] = locations_strings.encode("utf-16be") # Read the locations.
		locations["nullbyte_%s_locations" % numbers] = u16(0) # Null byte for the locations.

	return locations

"""Add the source pictures."""

def make_source_pictures(source_table, data):
	source_pictures = collections.OrderedDict()
	dictionaries.append(source_pictures)

	source_articles = []
	
	"""These are the news sources which will get a custom news picture from them."""

	sources = ["ANP", "ap", "dpa", "reuters", "SID", "ZEIT ONLINE", "news24", "NU.nl"]

	for article in data.values():
		if article[9] not in source_articles:
			if article[9] in sources:
				source_articles.append(article[9])

				source_table["pictures_size_%s" % article[9]] = u32(os.path.getsize("./logos/%s.jpg" % article[9]))
				source_table["pictures_offset_%s" % article[9]] = offset_count()

				with open("./logos/%s.jpg" % article[9], "rb") as source_file:
					source_pictures["logo_%s" % article[9]] = source_file.read()

	return source_pictures

"""Add the pictures."""

def make_pictures(pictures_table, data):
	pictures = collections.OrderedDict()
	dictionaries.append(pictures)

	numbers = 0

	for article in data.values():
		numbers += 1
		if article[4] != 0:
			pictures_table["pictures_%s_offset" % numbers] = offset_count() # Offset for the pictures.
			pictures["pictures_%s_read" % numbers] = article[4] # Read the pictures.
			pictures["nullbyte_%s_pictures" % numbers] = u8(0) # Null byte for the pictures.

			for types in ["captions", "credits"]:
				if pictures_table["%s_%s_offset" % (types, numbers)] != u32(0) and pictures_table["%s_%s_size" % (types, numbers)] == u32(0):
					pictures_table["%s_%s_offset" % (types, numbers)] = u32(0)

	return pictures

"""Add RiiConnect24 text."""

def make_riiconnect24_text():
	riiconnect24_text = collections.OrderedDict()
	dictionaries.append(riiconnect24_text)
	
	"""The RiiConnect24 text is used just to say it's our file."""

	riiconnect24_text["padding"] = u32(0) * 4 # Padding.
	riiconnect24_text["text"] = "RIICONNECT24" # Text.

"""Write everything to the file."""

def write_dictionary(mode):
	newsfilename = "news.bin.%s.%s.%s" % (str(datetime.utcnow().hour).zfill(2), mode, system)

	for dictionary in dictionaries:
		for values in dictionary.values():
			with open(newsfilename + "-1", "a+") as dest_file:
				dest_file.write(values)

	with open(newsfilename + "-1", "rb") as source_file:
		read = source_file.read()

	with open(newsfilename + "-2", "w+") as dest_file:
		dest_file.write(u32(512))
		dest_file.write(u32(len(read) + 12))
		dest_file.write(binascii.unhexlify(format(binascii.crc32(read) & 0xFFFFFFFF, '08x')))
		dest_file.write(read)

	FNULL = open(os.devnull, "w+")

	subprocess.call(["mono", "--runtime=v4.0.30319", "%s/DSDecmp.exe" % dsdecmp_path, "-c", "lz10", newsfilename + "-2", newsfilename], stdout=FNULL, stderr=subprocess.STDOUT)

	with open(newsfilename, "rb") as source_file:
		read = source_file.read()

	with open(key_path, "rb") as source_file:
		private_key_data = source_file.read()

	private_key = rsa.PrivateKey.load_pkcs1(private_key_data, "PEM")

	signature = rsa.sign(read, private_key, "SHA-1")

	with open(newsfilename, "wb") as dest_file:
		dest_file.write(binascii.unhexlify("0".zfill(128)))
		dest_file.write(signature)
		dest_file.write(read)

	"""Remove the rest of the other files."""

	os.remove(newsfilename + "-1")
	os.remove(newsfilename + "-2")