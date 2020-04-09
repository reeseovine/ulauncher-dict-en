import os
import sys
from os.path import join

from ulauncher.search.SortedList import SortedList
from Levenshtein import ratio
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction

FILE_PATH = os.path.dirname(sys.argv[0])


class Entry:
	""" Container class for dictionary entries
	"""

	def __init__(self, word, pos, defn):
		self.word = word
		self.pos  = pos
		self.defn = defn

	def get_search_name(self):
		""" Called by `ulauncher.search.SortedList` to get the string
		that should be used in searches
		"""
		return self.word


class DictionaryExtension(Extension):
	def __init__(self):
		super().__init__()

		self._load_dict_txt()
		self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

	def _load_dict_txt(self):
		""" Read the data file and load to memory
		"""
		self.dictionary = []
		with open(join(FILE_PATH, "dict.txt"), "r") as f:
			for line in f.readlines():
				word, pos, defn = line.strip().split("\t")
				entry = Entry(word, pos, defn)
				self.dictionary.append(entry)


class KeywordQueryEventListener(EventListener):
	def on_event(self, event, extension):
		items = []
		arg = event.get_argument()
		if arg:
			result_list = WordSorter(arg, min_score=10, limit=10)
			result_list.extend(extension.dictionary)
			for entry in result_list:
				if len(entry.pos) > 0:
					name = entry.word + " ("+ entry.pos +")"
				else:
					name = entry.word
				
				items.append(
					ExtensionResultItem(
						icon = os.path.join(FILE_PATH, "images/icon.png"),
						name = name,
						description = format_defn(entry.defn),
						on_enter = OpenUrlAction(gen_wiktionary_url(entry.word)),
					)
				)
		return RenderResultListAction(items)


class WordSorter(SortedList):
	def __init__(self, query, min_score=30, limit=9):
		super().__init__(query, min_score, limit)
		self.query = query

	def append(self, result_item):
		score = self.get_score(result_item.get_search_name())
		if score >= self._min_score:
			result_item.score = -score  # use negative to sort by score in desc. order
			self._items.insert(result_item)
			while len(self._items) > self._limit:
				self._items.pop()  # remove items with the lowest score to maintain limited number of items

	def get_score(self, text):
		"""
		Uses Levenshtein's algorithm
		:returns: number between 0 and 100
		"""
		if not self.query or not text:
			return 0

		query = self.query.lower()
		text = text.lower()
		score = ratio(query, text) * 100

		if not text.startswith(query):
			return 0

		return min(100, score)


def format_defn(defn):
	defn = defn.split("; ",1)[0]
	if len(defn) >= 80:
		defn = defn[:80] + "..."
	return defn

def gen_wiktionary_url(word):
	base_url = "https://en.wiktionary.org/wiki/"
	word_fmt = word.replace(" ", "_").lower()
	return base_url + word_fmt


if __name__ == "__main__":
	DictionaryExtension().run()
