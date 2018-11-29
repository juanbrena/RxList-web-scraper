#!/usr/bin/env python

#This script first collects medications found in RxList medication database in alphabetical order.
#After collecting medications it will check if the collected medication returns a valid search because
#Rxlist.com store their medication either by their generic name or brand name.

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def simple_get(url):
	"""
	Attempts to get the content at `url` by making an HTTP GET request.
	If the content-type of response is some kind of HTML/XML, return the
	text content, otherwise return None.
	"""
	try:
		with closing(get(url, stream=True)) as resp:
			if is_good_response(resp):
				return resp.content
			else:
				return None

	except RequestException as e:
		log_error('Error during requests to {0} : {1}'.format(url, str(e)))
		return None


def is_good_response(resp):
	"""
	Returns True if the response seems to be HTML, False otherwise.
	"""
	content_type = resp.headers['Content-Type'].lower()
	return (resp.status_code == 200 
			and content_type is not None 
			and content_type.find('html') > -1)


def log_error(e):
	"""
	It is always a good idea to log errors. 
	This function just prints them, but you can
	make it do anything.
	"""
	print(e)

def get_med_names(letter):
	url = 'https://www.rxlist.com/drugs/alpha_'+letter+'.htm'
	response = simple_get(url)

	if response is not None:
		html = BeautifulSoup(response, 'html.parser')
		names = set()
		for li in html.select('li'):
			for name in li.text.split('\n'):
				if len(name) > 1:
					if name[0] == letter.upper():
						names.add(name.strip())

		return list(names)

	raise Exception('Error retrieving contents at {}'.format(url))

def find_shortest_med(med):
	first_parenthesis_position = med.find('(')
	second_parenthesis_position = med.find(')')

	if first_parenthesis_position == -1:
		return med
	
	first_part_of_med = med[0:first_parenthesis_position]

	second_part_of_med = med[first_parenthesis_position+1:second_parenthesis_position]

	if len(first_part_of_med) < len(second_part_of_med):
		return first_part_of_med
	elif len(second_part_of_med) < len(first_part_of_med):
		return second_part_of_med
	else:
		return first_part_of_med

def check_if_valid_rxlist_url(med):
	url = convert_to_valid_rxlist_url(med)
	
	page_responce = simple_get(url)
	#print("The medicine being searched: " + med)
	#print("The url being searched: " + url)
	
	if page_responce is not None: 
		html = BeautifulSoup(page_responce, "html.parser")
		for i, h1 in enumerate(html.select("h1")):
			if h1.text != "RxList Page Not Found":
				print(med)

def convert_to_valid_rxlist_url(med):
	med = med.lower()
	med = med.replace(" ","-")
	url = 'https://www.rxlist.com/'+med+'-drug.htm'
	if url.find('--') != -1:
		url = url.replace("--","-")
	if url.find('--') != -1:
		url = url.replace("--","-")
	return url 

def remove_doubles(duplicate): 
    final_list = [] 
    for num in duplicate: 
        if num not in final_list: 
            final_list.append(num) 
    return final_list 	

#MAIN
if __name__ == '__main__':
	i = 0
	alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
	
	while i < 26:
		letter = alphabet[i]
		med_names = get_med_names(letter)

		med_results = []

		for med in med_names:
			med_results.append(med)

		short_med_results = []
		
		for med in med_results:
			if med.find('- FDA') != -1:
				shortest_med = find_shortest_med(med)
				if shortest_med not in short_med_results:
					shortest_med = shortest_med.rstrip()
					short_med_results.append(shortest_med)

			if med.find('- MULTUM') != -1:
				shortest_med = find_shortest_med(med)
				if shortest_med not in short_med_results:
					shortest_med = shortest_med.rstrip()
					short_med_results.append(shortest_med)

		short_med_results2 = list(set(short_med_results))
		short_med_results2.sort()

		for med in short_med_results2:
			check_if_valid_rxlist_url(med)
		i+=1























