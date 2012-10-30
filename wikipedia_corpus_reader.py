#!/usr/bin/env python
# encoding: utf-8
"""
wikipedia_corpus_reader.py

Created by Ari Ehrmann.
Email address: <ari.ehrmann@gmail.com>
LING 131A Final Project: Wikipedia Language Processor
"""

import re
import nltk
import subprocess 
import os
import shutil
from collections import defaultdict
from nltk.corpus import PlaintextCorpusReader

class WikipediaCorpusReader(PlaintextCorpusReader):
	"""
	Reader specifically for use with Wikipedia articles. The reader accepts 
	a topic as input, then performs processing to create the directories and 
	files containing the Wikipedia pages for the reader to process.
	
	Processes the initial Wikipedia page, scanning for all links to other
	Wikipedia pages and scans the content of those pages.
	"""
	BASE_WGET_COMMAND = r'wget --random-wait -qO- '
	BASE_WIKIPEDIA_URL = r'http://en.wikipedia.org/wiki/'
	
	def __init__(self, topic):
		"""
		Construct a new WikipediaCorpusReader for a topic and a set of 
		subtopics. Example usage:
			
			>>> wiki_reader = WikipediaCorpusReader("The house of representatives")
		
		:param topic: The text for the topic of this WikipediaCorpusReader
		:type topic: str
		
		:raise ValueError: If the topic string does not correspond to a single Wikipedia topic
		"""
		# Generate a well-formed topic name and use it as the root 
		# directory's name
		self._root_topic = self._wikipedia_topic(topic)
		self._root = self._root_topic
		
		# Save the root topic's URL and write it's text to the appropriate file
		self._root_topic_url = self._url_for_topic(self._root_topic)
		
		root_html = self._html_for_url(self._root_topic_url) # Download the root topic's HTML
		if root_html is None:
			raise ValueError('Proper article for %s could not be found' % self._root_topic_url)
		if not self._is_valid_article(root_html):
			raise ValueError('%s returns more than one topic on Wikipedia' % self._root_topic_url)
		self._root_fileid = self._fileid_for_url(self._root_topic_url)
		
		
		# Create the root directory if it doesn't already exist
		if not os.path.exists(self._root):
			os.mkdir(self._root)
		self._generate_file_for_url(self._root_topic_url, root_html)
		
		self._urls_by_section = {}
		# We need to do initial searching for the Introduction section since it's not
		# formatted in the same way as the sections
		html_introduction = re.search(r'<!-- bodycontent -->(.*?)<h2>Contents</h2>', root_html, re.DOTALL).group(1)
		urls_introduction_subtopics = self._subtopic_urls(html_introduction)
		self._urls_by_section["Introduction"] = urls_introduction_subtopics
		
		# Parse through the HTML for the source for each section
		html_all_sections = re.findall(r'<span class="mw-headline"(.*?)<h\d>', root_html, re.DOTALL)
		
		# Parse the HTML for the section title and collect any links to other Wikipedia pages
		for html_section in html_all_sections:
			section_title = re.search(r' id="(?:.*?)">(.*?)</span></h\d>', html_section, re.DOTALL).group(1)
			section_title = self._cleaned_section_title(section_title)
			urls_section_subtopics = self._subtopic_urls(html_section)
			self._urls_by_section[section_title] = urls_section_subtopics
		
		self._fileids_by_section = defaultdict(list)
		fileids_list = []
		self._fileid_to_url = {}
		for section in self._urls_by_section:
			for url in self._urls_by_section[section]:
				fileid = self._fileid_for_url(url)
				self._fileids_by_section[section].append(fileid)
				fileids_list.append(fileid)
				self._fileid_to_url[fileid] = url
				
		self._invalid_fileids = []
		
		nltk.corpus.PlaintextCorpusReader.__init__(self, self._root, fileids_list)
	
##############################################################################################
# 									Private methods											#
#############################################################################################
				
	def _wikipedia_topic(self, topic):
		"""
		Converts a topic into a well-formed Wikipedia path suffix.
		E.g. "clive owen" becomes "Clive_Owen"
		
		:param topic: A string representing a topic
		:type topic: str
		
		:return: a topic appropriate for the end of a Wiki URL
		:rtype: str
		"""
		suffix = re.split(r'[_ ]', topic)							# split on spaces or underscores
		suffix = '_'.join([word.capitalize() for word in suffix])	# capitalize every word
		return suffix
		
	def _fileid_for_url(self, url):
		"""
		Converts a Wikipedia url into a filename.
		
		:param url: a full URL
		:type url: str
		
		:return: a filename for saving the plaintext of the URL's content
		:rtype: str
		"""
		suffix = url.split("/")[-1]									# Only take the last piece of the URL
		filename = re.sub(r'[()]|%(?:[A-Z]|\d){2}', r'', suffix) 	# Remove any parentheses and escape codes
		filename = re.sub(r'__', r'_', filename)					# Collapse any __ to _ 
		return filename + ".txt"
	
	def _url_for_topic(self, topic):
		"""
		Generates the full URL for a topic. 
		
		:param topic: a topic of a Wikipedia article
		:type topic: str
		
		:return: a full URL for accessing a Wiki article
		:rtype: str
		"""
		wiki_topic = self._wikipedia_topic(topic)
		return self.BASE_WIKIPEDIA_URL + wiki_topic
	
	def _cleaned_section_title(self, title):
		"""
		Santizes the text from a section title by removing certain characters.
		
		:param title: section text for a title
		:type title: str
		
		:return: a cleaned section title
		:rtype: str
		"""
		new_title = self._wikipedia_topic(title)							# Create a topic out of the title
		new_title = re.sub(r'[()]', r'', new_title) 						# Remove all parentheses
		new_title = re.sub(r'__', r'_', new_title)							# Collapse __ to _
		new_title = re.sub(ur'\xe2\x80\x93', r'_', new_title, re.UNICODE)	# Remove unicode dash symbol from string
		return new_title
		
	def _html_for_url(self, url):
		"""
		Using wget(a command line tool), downloads and returns the html content from the given url.
		
		:param url: a full URL to a Wikipedia page
		:type url: str
		
		:return: HTML source from the URL
		:rtype: str
		""" 
		escaped_url = re.sub(r'([()])', r'\\\1', url)						# Escape all parentheses
		try:
			html = subprocess.check_output(self.BASE_WGET_COMMAND + escaped_url, shell=True)
		except subprocess.CalledProcessError:
			return None
		return html
		
	
	
	def _subtopic_urls(self, html):
		"""
		Returns all links to other Wikipedia pages within the HTML source passed in.
		
		:param html: HTML source code
		:type html: str
		
		:return: a list of URLs that link to other Wiki articles within the HTML source
		:rtype: list of str 
		"""
		links = re.findall(r'href="(/wiki/[^\'" >]+)"', html)					# Find all links with "wiki" in them
		wiki_links = set(["http://en.wikipedia.org"+link for link in links])	# Create absolute URLs for each link
		wiki_page_keywords = re.compile(r'.*/wiki/(Wikipedia|File|Special|Help|Category|Talk|Portal|Main_Page|Template|Template_talk)')
		wiki_links = [link for link in wiki_links if not wiki_page_keywords.match(link)]	# Filter out links to standard Wikipedia pages
		return wiki_links
		
	def _generate_file_for_url(self, url, html):
		"""
		Cleans the passed in HTML source and writes it to a file whose name is generated by another function. 
		Returns the name of the newly created file's name or None if the topic did not have a valid article
		associated with it on Wikipedia.
		
		:param url: A full URL for a Wikipedia page
		:type url: str
		
		:param html: HTML source from the Wikipedia page
		:type html: str
		
		:return: file name of the newly created file
		:rtype: str
		"""
		# If Wikipedia doesn't have an article for the given topic, return None
		if not self._is_valid_article(html):
			self._invalid_fileids.append(self._fileid_for_url(url))
			return None
		self.reload_root()											# Reload the root directory in case it was deleted
		filename = self._root + "/" + self._fileid_for_url(url)		# Generate the fileid for the URL
		if not os.path.isfile(filename):							# If the file doesn't already exist
			text = self._clean_html_and_wikipedia_content(html)		# Clean the text
			textfile = open(filename, r'w')			
			textfile.write(text)	
			textfile.close()
		return filename
	
	def _load_all_urls(self, urls):
		"""
		Downloads the HTML source of every URL given then cleans and saves the
		text to a file. Returns the list of filenames. 
		
		:param urls: A collection of URLS
		:type urls: list of str
		
		:return: file paths for all created files
		:rtype: list of str
		"""
		paths = []
		for url in urls:
			filename = self._fileid_for_url(url)
			if filename in self._invalid_fileids:
				continue
			if not os.path.isfile(self._root + "/" + filename):		# If the file hasn't already been downloaded
				print "Loading:", filename		
				html = self._html_for_url(url)						# Grab the HTML
				result = self._generate_file_for_url(url, html)		# Generate the file with text from the HTML
				if result is not None:							
					paths.append(result)
			else:
				paths.append(filename)
		return paths
	
	def _is_valid_article(self, html):
		"""
		Checks whether the article contains standard Wikipedia page or invalid text
		
		:param html: HTML source
		:type html: str
		
		:return: Boolean indicating whether the article's page is valid
		:rtype: Boolean
		"""
		if re.search(r'<a href="/wiki/Special:Categories"', html):
			if not re.search(r'/wiki/Category:Disambiguation_pages', html):
				return True
		return False
	
	def _clean_html_and_wikipedia_content(self, html):
		"""
		Extracts the article's body HTML and throroughly sanitizes it.
		
		:param html: HTML source from a Wikipedia article's body content
		:type html: str
		
		:return: Cleaned body content from the given HTML source
		:rtype: str
		"""
		# Extract only the body content from the article
		body = re.search(r'<!-- bodyContent -->(.*)<!-- /bodyContent -->', html, re.DOTALL).group(1)
		# Remove boiler plate from HTML
		body = re.sub(r'<!-- tagline -->.*?<!-- /tagline -->', r'', body, re.DOTALL)
		body = re.sub(r'<!-- subtitle -->.*?<!-- /jumpto -->', r'', body, re.DOTALL)
		body = re.sub(r'<h2>Contents</h2>', r'', body, re.DOTALL)				# Remove the word "Contents"
		cleaned_body = nltk.clean_html(body)									# Clean out the HTML tags
		cleaned_body = ' '.join(cleaned_body.split()[10:])						# Collapse all whitespace into spaces
																				# and remove the 1st 9 words
		cleaned_body = re.sub(r'http.*? ', r'', cleaned_body, re.DOTALL)		# Remove stray URLS
		cleaned_body = re.sub(r'&#\d{3};|&\w+?;', r'', cleaned_body)			# Remove escape characters
		cleaned_body = ''.join([x for x in cleaned_body if ord(x) < 128])		# Remove all Unicode characters
		cleaned_body = re.sub(r'\[ (\d+|\w+) \]', r'', cleaned_body)			# Remove edit button text and citations
		cleaned_body = re.sub(r'[\'()^"#:\\;]', r' ', cleaned_body)				# Remove extraneous punctuation
		cleaned_body = re.sub(r' \.| \. ', r' ', cleaned_body)					# Remove stray periods
		cleaned_body = re.sub(r'.\. ', r' ', cleaned_body)						# Remove sentence-ending periods
		cleaned_body = re.sub(r' ,| , |, ', r' ', cleaned_body)					# Remove stray commas
		cleaned_body = re.sub(r' /| / |/ ', r' ', cleaned_body)					# Remove stray slashes
		cleaned_body = re.sub(r'\s{2,}', r' ', cleaned_body)					# Replace large whitespace left from previous removals	
		cleaned_body = re.sub(r'Wikimedia Commons.*?pages', r'', cleaned_body) 	# Remove more boilerplate						
		return cleaned_body
	
	# Override
	# Taken from CategorizedPlaintextCorpusReader
	def _resolve(self, fileids, sections):
		"""
		Returns the appropriate fileids to the caller, after downloading
		and storing their text to files.
		
		:param fileids: single fileids or list of fileids
		:type fileids: list of str
		
		:param sections: single sections or list of sections
		:type sections: list of str
		
		:return: fileids contained in the specified fileids or sections
		:rtype: list of str
		"""
		if fileids is not None and sections is not None:
			raise ValueError('Specify fileids or categories, not both')
		urls = []
		if sections is not None:
			if isinstance(sections, basestring):
				urls.extend(self._urls_by_section[sections])
			else:
				for section in sections:
					urls.extend(self._urls_by_section[section])
			self._load_all_urls(urls)
			return [fileid for fileid in self.fileids(sections) if fileid not in self._invalid_fileids]
		elif fileids is not None:
			if isinstance(fileids, basestring):
				urls = self._fileid_to_url[fileids]
				self._load_all_urls([urls])
				if fileids not in self._invalid_fileids:
					return [fileids] 
				else: 
					return None
			else:
				urls = [url for id, url in self._fileid_to_url.iteritems() if id in fileids]
				self._load_all_urls(urls)
			return [fileid for fileid in fileids if fileid not in self._invalid_fileids]
		else:
			self._load_all_urls(self._fileid_to_url.values())
			return [fileid for fileid in self._fileid_to_url.keys() if fileid not in self._invalid_fileids]
	
	
##############################################################################################
# 									Public methods											#
#############################################################################################
	def root_topic(self):
		"""
		Returns the root topic specified when constructed
		
		:return: The root topic
		:rtype: str
		"""
		return self._root_topic
	
	def sections(self):
		"""
		Returns the titles of the sections on the topic's Wikipedia page.
		
		:return: list of section titles
		:rtype: list of str
		"""
		return [section for section in self._fileids_by_section]
	
	def topics(self, sections=None):
		"""
		Returns a list of topic names (by section, if specified).
		
		:param sections: single section or list of sections
		:type sections: single str or list of str
		
		:return: list of topic names
		:rtype: list of str
		"""
		if sections is None:
			return sorted([fileid[:-4] for fileid in self._fileids])
		elif isinstance(sections, basestring):
			return sorted([fileid[:-4] for fileid in self._fileids_by_section[sections]])
		else:
			fileids = []
			for section in sections:
				fileids.extend(self._fileids_by_section[section])
			return sorted([fileid[:-4] for fileid in fileids])
			
	def fileids(self, sections=None):
		"""
		Returns a list of fileids (by section, if specified)
		
		:param sections: single section or list of sections
		:type sections: single str or list of str
		
		:return: list of fileids
		:rtype: list of str
		"""
		if sections is None:
			return sorted([fileid for fileid in self._fileids if fileid not in self._invalid_fileids])	
		elif isinstance(sections, basestring):
			if sections in self._urls_by_section:
				return sorted([fileid for fileid in self._fileids_by_section[sections] if fileid not in self._invalid_fileids])
			else:
				raise ValueError('Section %s not found' % sections)
		else:
			all_fileids_for_sections = []
			for section in sections:
				all_fileids_for_sections.extend([fileid for fileid in self._fileids_by_section[section] if fileid not in self._invalid_fileids])
			return sorted(all_fileids_for_sections)
				
	
	def raw(self, fileids=None, sections=None):
		"""
		Returns the raw string data stored in the specified sections/files
		
		:param fileids: single fileid or list of fileids
		:type fileids: single str or list of str
		
		:param sections: single section or list of sections
		:type sections: single str or list of str
		
		:return: conglomeration of raw text from all fileids and sections
		:rtype: str
		"""
		return PlaintextCorpusReader.raw(
			self, self._resolve(fileids, sections))
			
	def words(self, fileids=None, sections=None):
		"""
		Returns a tokenized list of strings from the data stored in the 
		specified sections/files
		
		:param fileids: single fileid or list of fileids
		:type fileids: single str or list of str
		
		:param sections: single section or list of sections
		:type sections: single str or list of str
		
		:return: conglomeration of word token from all fileids and sections
		:rtype: list of str
		"""
		return nltk.corpus.PlaintextCorpusReader.words(
			self, self._resolve(fileids, sections))
				
	def reader_with_topic(self, topic):
		"""
		Returns a new WikipediaCorpusReader instance with the specified topic
		
		:param topic: topic on Wikipedia
		:type topic: str
		
		:return: a new instance of WikipediaCorpusReader with the root topic set to 
		the given topic
		:rtype: WikipediaCorpusReader
		"""
		return WikipediaCorpusReader(topic) 
	
	def topic_tagged_words(self, fileids=None, sections=None):
		"""
		Returns a generator of words paired with their topics, e.g.
		('death', 'Global_Warming'), for the specified sections or 
		fileids 
		
		:param fileids: single fileid or list of fileids
		:type fileids: single str or list of str
		
		:param sections: single section or list of sections
		:type sections: single str or list of str
		
		:return: generator of words, tagged with topic title
		:rtype: generator of tuples (str, str)
		"""
		fileids = self._resolve(fileids, sections)
		for fileid in fileids:
			for word in self.words(fileids=fileid):
				yield ((word, fileid[:-4]))

	def delete_corpus(self):
		"""
		Deletes the directory created by this instance and its contents
		"""
		if not os.path.exists(self._root):
			shutil.rmtree(self._root)
		
	def reload_root(self):
		"""
		Recreates the root directory if it does not exist.
		"""
		if not os.path.exists(self._root):
			os.mkdir(self._root)

if __name__ == '__main__':
	print "Try running main.py instead"