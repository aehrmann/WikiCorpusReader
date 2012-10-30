#!/usr/bin/env python
# encoding: utf-8
"""
wikipedia_topic_analyzer.py

Created by Ari Ehrmann.
Email address: <ari.ehrmann@gmail.com>
LING 131A Final Project: Wikipedia Language Processor
"""

from collections import defaultdict
from operator import itemgetter
from nltk.corpus import stopwords
import re
import string

class WikipediaTopicAnalyzer(object):
	"""
	WikipediaTopicAnalyzer is an object that performs linguistic
	analysis with a given set of Wikipedia articles. Made for use 
	with WikipediaCorpusReader.
	"""
	def __init__(self, topic_tagged_words):
		"""
		Constructs a new instance of WikipediaTopicAnalyzer. Filters out stop words.
		Example usage:
			
			>>> analyzer = WikipediaTopicAnalyzer(<list of tagged words>)
			
		:param topic_tagged_words: 	a list of topic-tagged-words in the format 
									of (word, topic).
		"""
		
		# Filters out the words given by removing stopwords, punctuation, words consisting of a single 
		# letter or single number, and the word 'ISBN'
		excluded = set(stopwords.words('english')).union(set([",",".","/","-","?","=","[","]","+","/?","%","isbn"]))
		
		tagged_words = [tag_pair for tag_pair in topic_tagged_words \
		 							if tag_pair[0].lower() not in excluded and \
		 							not re.match(r'^\d$', tag_pair[0]) and \
		 							not re.match(r'^\w$', tag_pair[0])]		
		
		self._word_topic_count = defaultdict(dict)
		self._topics = []
		
		# Create dictionary of word -> dictionary of topic -> count for word
		for word, topic in tagged_words:
			if not word in self._word_topic_count:
				self._word_topic_count[word] = defaultdict(int)
			self._word_topic_count[word][topic] += 1
		
			# Store a list of topics
			if topic not in self._topics:
				self._topics.append(topic)

	def topics(self):
		"""
		Returns the topics associated with the words given to this instance
		
		:return: list of topic titles
		:rtype: list of str
		"""
		return self._topics
	
	def most_frequent_words(self, n=10, topics=None):
		"""
		Returns the n most common words, i.e. those found in the most
		articles. Returns in lowercase form and sorted by number of articles.
		
		:param n: the number of words to display
		:type n: int
		
		:param topics: a list of articles to calculate the most common words from
		:type topics: list
		
		:return: list of the most frequent words in the given topics (or all if unspecified)
		:rtype: list of (str, int) 
		"""
		if topics is None:
			counts = []
			for word in self._word_topic_count:									# For each word
				occurrences = 0													# Set counter to 0
				for topic in self._word_topic_count[word]:						# For each topic the word appears in
					occurrences += self._word_topic_count[word][topic]			# Increment the counter by the # of 
																				# 	times the word appears in the topic
				counts.append((word,occurrences))								# Append a tuple of (word, count)
		else:
			counts = []
			if isinstance(topics, basestring):
				for word in self._word_topic_count:								# For each word
					occurrences = 0												# Set counter to 0
					for topic in self._word_topic_count[word]:					# For each topic the word appears in
						if topic == topics:										# If the topic is the one given
							occurrences += self._word_topic_count[word][topic]	# Increment the counter by the occurrences
																				# 	of the word in that topic
					counts.append((word,occurrences))							# Append a tuple of (word, count)
			else:
				for word in self._word_topic_count:								# For each word
					occurrences = 0												# Set counter to 0
					for topic in self._word_topic_count[word]:					# For each topic the word appears in
						if topic in topics:										# If the topic is one of the given topics
							occurrences += self._word_topic_count[word][topic]	# Increment the counter by the occurrences
																				# 	of the word in that topic
					counts.append((word,occurrences))							# Append a tuple of (word, count)
		return sorted(counts, key=itemgetter(1), reverse=True)[:n]
	
	def most_frequent_words_by_topic(self, n=10, topics=None):
		"""
		Returns the n most common words in each topic.
		
		:param n: the number of words to display
		:type n: int
		
		:param topics: a list of topic names
		:type topics: list
		
		:return: a dictionary of the top n most frequent words for each topic (or all if unspecified)
		:rtype: dictionary of str -> list of (str, int)
		"""
		if topics is None:					# If no topics were specified
			topics = self._topics			# Set the topics to process to all topics
		common_words_by_topic = {}
		for topic in topics:
			# Set the value at each topic to be the most frequent word,count pairs for that topic
			print topic 
			common_words_by_topic[topic] = self.most_frequent_words(n, topics=topic)
			print common_words_by_topic[topic]
		return common_words_by_topic
	
	def most_frequent_terms(self, n=10, topics=None):
		"""
		Returns the n most common "terms", i.e. capitalized words found in the most
		articles if they appear more than once.
		
		:param n: the number of "terms" to display
		:type n: int
		
		:param topics: a list of topic names
		:type topics: list
		
		:return: a list of the most frequent "terms" from the specified topics (or all if unspecified)
		:rtype: list of (str, int) 
		"""
		# Only look through capitalized words
		capitalized_words = [word for word in self._word_topic_count if word[0] in string.uppercase]
		
		if topics is None:
			counts = []
			for word in capitalized_words:										# For each capitalized word
				occurrences = 0													# Set counter to 0
				for topic in self._word_topic_count[word]:						# For each topic the word appears in
					occurrences += self._word_topic_count[word][topic]			# Increment the counter by the # of 
																				# 	times the word appears in the topic
				if occurrences > 2:
					counts.append((word,occurrences))							# Append a tuple of (word, count)
		else:
			counts = []
			if isinstance(topics, basestring):
				for word in capitalized_words:									# For each capitalized word
					occurrences = 0												# Set counter to 0
					for topic in self._word_topic_count[word]:					# For each topic the word appears in
						if topic == topics:										# If the topic is the one given
							occurrences += self._word_topic_count[word][topic]	# Increment the counter by the occurrences
																				# 	of the word in that topic
					if occurrences > 2:
						counts.append((word,occurrences))						# Append a tuple of (word, count)
			
			else:
				for word in capitalized_words:									# For each word
					occurrences = 0												# Set counter to 0
					for topic in self._word_topic_count[word]:					# For each topic the word appears in
						if topic in topics:										# If the topic is one of the given topics
							occurrences += self._word_topic_count[word][topic]	# Increment the counter by the occurrences
																				# 	of the word in that topic
					if occurrences > 2:
						counts.append((word,occurrences))						# Append a tuple of (word, count)
				
		return sorted(counts, key=itemgetter(1), reverse=True)[:n]
		
	def most_frequent_terms_by_topic(self, n=10, topics=None):
		"""
		Returns the n most common "terms", i.e. capitalized words found in the most
		articles if they appear more than once, for each topic.
		
		:param n: the number of terms to display for each topic
		:type n: int
		
		:param topics: a list of topic names
		:type topics: list
		
		:return: a dictionary of lists of most frequent "terms" for each topic (or all if unspecified)
		:rtype: a dictionary of str -> (str, int)
		"""
		if topics is None:			# If no topics were specified
			topics = self._topics	# Set topics to be all topics
		frequent_terms = {}
		for topic in topics:
			# Set the value for the dictionary at each topic to be the list of most common terms
			frequent_terms[topic] = self.most_frequent_terms(n=n,topics=topic)
		return frequent_terms
	
	def topics_containing_words(self, words):
		"""
		Returns the topics in which every word specified is found
		
		:param words: a list of words for which to find common topics
		:type words: list of str
		
		:return: list of topics in which every word specified appears
		:rtype: list of str
		"""
		topics = []
		if isinstance(words, basestring):
			if words in self._word_topic_count:
				topics.extend(self._word_topic_count[words].keys())
		else:
			for word in words:
				if word in self._word_topic_count:
					topics.extend(self._word_topic_count[word].keys())
			topics = [topic for topic in topics if topics.count(topic) >= len(words)]
			
		return sorted(set(topics))

		
	def common_words_between_topics(self, topics=None):
		"""
		Returns words that are found in all given topics
		
		:param topics: a list of topic names
		:type topics: list
		
		:return: list of words that are found in every topic (or all if unspecified)
		:rtype: list of str 
		"""
		common_words = []
		if topics is None:
			topics = self._topics
		
		for word in self._word_topic_count:

			if set(topics).issubset(set(self._word_topic_count[word])):
				common_words.append(word)
		return sorted(common_words)

if __name__ == '__main__':
	print "Try running main.py instead"	