import time
import re
import urllib.request
from bs4 import BeautifulSoup
from string import ascii_lowercase

with open('dict.txt','a') as fout:
	for x in ascii_lowercase:
		print(x)
		with urllib.request.urlopen("http://www.mso.anu.edu.au/%7Eralph/OPTED/v003/wb1913_"+x+".html") as response:
			page = BeautifulSoup(str(response.read()), 'html.parser')
			i = 0
			for entry in page.find_all('p'):
				word = str(entry.b.text).replace("\\", "")
				pos  = str(entry.i.text).replace("\\", "")
				defn = str(entry.contents[3][2:]).replace("\\", "")

				if len(word) > 0 and len(defn) > 0:
					fout.write(word +"\t"+ pos +"\t"+ defn +"\n")
					i += 1

			print("Wrote", i, "entries.")

fout.close()
