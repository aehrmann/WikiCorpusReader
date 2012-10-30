#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Ari Ehrmann.
Email address: <ari.ehrmann@gmail.com>
LING 131A Final Project: Wikipedia Language Processor
"""
from pprint import pprint
from wikipedia_corpus_reader import WikipediaCorpusReader
from wikipedia_topic_analyzer import WikipediaTopicAnalyzer

def printHeader(text):
	print "#" * 100
	print text + '   ' + ('#' * (97-len(text)))
	print "#" * 100 + "\n"

def testCases():
	printHeader("WikipediaCorpusReader Test Cases")
	print ''
	
	printHeader("WikipediaCorpusReader instance with root topic 'Google':")
	reader = WikipediaCorpusReader("google")
	pprint(reader)
	print "Root topic is", reader.root_topic()
	print ''
	
	printHeader("Sections of Wiki page for 'Google':")
	pprint(reader.sections())
	print ''
	
	printHeader("Topics for all sections:")
	pprint(reader.topics())
	print ''
	
	printHeader("Topics for sections ['Philanthropy', 'Enterprise_Products', 'Googleplex']:")
	pprint(reader.topics(sections=['Philanthropy', 'Enterprise_Products', 'Googleplex']))
	print ''
	
	printHeader("Fileids for section 'Philanthropy':")
	pprint(reader.fileids(sections='Philanthropy'))
	print ''
	
	printHeader("Raw text for section 'Employees':")
	pprint(reader.raw(sections='Employees'))
	print ''
	
	printHeader("First 100 words for fileid 'Hitachi.txt':")
	pprint(list(reader.words(fileids='Hitachi.txt'))[:100])
	print ''
	
	printHeader("New instance of WikipediaCorpusReader with topic 'Hitachi':")
	new_reader = reader.reader_with_topic('Hitachi')
	pprint(new_reader)
	pprint(new_reader.sections())
	print ''
	
	printHeader("First 200 topic-tagged words for section 'Introduction:")
	pprint(list(reader.topic_tagged_words(sections='Introduction'))[:200])
	print ''
	
	print "#" * 100
	print "#" * 100
	print "#" * 100 + "\n"
	
	printHeader("WikipediaTopicAnalyzer Test Cases")
	print ''
	
	printHeader("WikipediaTopicAnalyzer instance with topic-tagged words from the above corpus reader's\nsections ['Philanthropy', 'Enterprise_Products', 'Googleplex']:'")
	tagged_words = reader.topic_tagged_words(sections=['Philanthropy', 'Enterprise_Products', 'Googleplex'])
	analyzer = WikipediaTopicAnalyzer(tagged_words)
	pprint(analyzer)
	print ''
	
	printHeader("Topics in the topic analyzer:")
	pprint(analyzer.topics())
	print ''
	
	printHeader("Top 30 most frequent words among all topics:")
	pprint(analyzer.most_frequent_words(n=30))
	print ''
	
	printHeader("Top 30 most frequent words from topics ['Google_Mini', 'Megawatt']:")
	pprint(analyzer.most_frequent_words_by_topic(n=30, topics=['Google_Mini', 'Megawatt']))
	print ''
	
	printHeader("Top 30 most frequent terms from topics ['Google_Mini', 'Megawatt']:")
	pprint(analyzer.most_frequent_terms(n=30, topics=['Google_Mini', 'Megawatt']))
	print ''
	
	printHeader("Top 30 most frequent terms by topic from topics ['Google_Mini', 'Megawatt']:")
	pprint(analyzer.most_frequent_terms_by_topic(n=30, topics=['Google_Mini', 'Megawatt']))
	print ''
	
	printHeader("Topics containing the words ['internet', 'electric']:")
	pprint(analyzer.topics_containing_words(['internet','electric']))
	print ''
	
	printHeader("Common words between topics ['Google_Mini', 'Megawatt']:")
	pprint(analyzer.common_words_between_topics(['Google_Mini', 'Megawatt']))
	print ''
	
def interactive():
	reader = None
	
	while reader is None:
		topic = raw_input("Please enter a topic to search on Wikipedia: ")
		try:
			reader = WikipediaCorpusReader(topic)
		except ValueError:
			reader = None
			print "Invalid topic. Please try again."
		
	print "Topic is", reader.root_topic()
	
	message = "Options:\n1) See sections\n2) See all topics\n3) See topics for a section\n4) See all fileids\n" + \
				"5) See fileids for a section\n6) See first 100 words for sections\n7) See first 100 topic-tagged " + \
				"words for a section\n8) Exit\n"
	
	choice = input(message)
	sections = reader.sections()
	while choice != 8:
		if choice == 1:
			print "Sections:"
			pprint(sections)
			print ''
			
		elif choice == 2:
			print "All topics:"
			pprint(reader.topics())
			print ''
			
		elif choice == 3:
			section = raw_input("Enter a section: ")
			print "Topics in section", section
			if section not in sections:
				print section + " is not an option\nPlease pick from " + sections	
			else:
				pprint(reader.topics(sections=section))
			print ''
				
		elif choice == 4:
			print "All fileids"
			pprint(reader.fileids())
			print ''
			
		elif choice == 5:
			section = raw_input("Enter a section: ")
			print "Topics in section", section

			if section not in sections:
				print section + " is not an option\nPlease pick from " + sections	
			else:
				pprint(reader.fileids(sections=section))
			print ''
		
		elif choice == 6:
			section = raw_input("Enter a section: ")
			print "First 100 words in section", section
			if section not in sections:
				print section + " is not an option\nPlease pick from " + sections	
			else:
				pprint(list(reader.words(sections=section))[:100])
			print ''
			
		elif choice == 7:
			section = raw_input("Enter a section: ")
			print "First 100 topic-tagged words in section", section
			if section not in sections:
				print section + " is not an option\nPlease pick from " + sections	
			else:
				pprint(list(reader.topic_tagged_words(sections=section))[:100])
			print ''
			
		elif choice == 8:
			return
		else:
			print "Invalid choice. Please choose a number 1-8.\n"
		
		choice = input(message)
	

if __name__ == '__main__':
	choice = None
	print "Welcome to the main function for Ari Ehrmann's LING131A Final Project!"	
	while choice is None:
		choice = input("Choose an option to continue:\n" + "1) Display test cases\n" + "2) Interactive session\n")
		if choice == 1:
			testCases()
		elif choice == 2:
			interactive()
		else:
			print "Only options are 1 and 2! Try again.\n"
			choice = None
	
	