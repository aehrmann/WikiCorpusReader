Wikipedia Corpus Reader
=======================
Copyright (C) 2011-2013 Ari Ehrmann

Wikipedia Corpus Reader is a grouping of modules that downloads the text of articles
from Wikipedia associated with a given topic and analyzes the text data using the open-source
Natural Language Toolkit (http://nltk.org/)


Run main.py to see either:
--------------------------
1. Test cases for both WikipediaCorpusReader and WikipediaTopicAnalyzer or
2. Run an interactive session with the WikipediaCorpusReader (limited
	functionality)

Dependencies:
-------------
* wget command must be installed, as it is used to scrape the Wikipedia pages
* NLTK must be installed and on user's PYTHONPATH 

*Note that there is a corpus in this folder associated with the term "Progressivism." 
Once a corpus is generated generated, it will stay in the folder. To
see how the corpus is dynamically generated, run the interactive session.*

Acknowledgements:
-----------------
The team at NLTK (http://nltk.org/)