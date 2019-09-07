import json
import re
import os
import requests
from collections import Counter
from nltk.corpus import stopwords
from math import log10
from collections import OrderedDict

"""
This word list contains terms that we want to find
in n-gram phrases or as part (prefix/suffix) of words
"""
ngramwordlist = ['specimen', 'specimens', 'type', 'types', 'typical', 'typify', 'typifies', 'typifying', 'species', 'genus', 'genera', 'form', 'subspecies', 'ecotype', 'ecotypes']

"""
The search function takes the uri for the request
and a term for the specific article. It changes the
global variables that represent the metadata for that
article based on the result from the query.
"""
def search(uri, term):
	query = json.dumps({"query": {"bool": {"must": [{"match_phrase": {"article.article-meta.article-id.#text": term}}]}},"from": 0,"size": 1,"_source": ["article.article-meta.title-group.article-title","article.article-meta.article-categories.subj-group.subject","article.article-meta.article-id.#text","article.article-meta.contrib-group","article.journal-meta.journal-title","article.article-meta.year"]})
	response = requests.get(uri, data=query)
	results = json.loads(response.text)
	try:
		global doi
		doi = results['hits']['hits'][0]['_source']['article']['article-meta']['article-id'][0]['#text']
	except:
		global doi
		doi = results['hits']['hits'][0]['_source']['article']['article-meta']['article-id']['#text']
	try:
		global journal
		journal = results['hits']['hits'][0]['_source']['article']['journal-meta']['journal-title']
	except:
		global journal
		journal = ""
	try:
		global title
		title = results['hits']['hits'][0]['_source']['article']['article-meta']['title-group']['article-title']
	except:
		global title
		title = ""
	try:
		global subject
		subject = results['hits']['hits'][0]['_source']['article']['article-meta']['article-categories']['subj-group']['subject']
	except:
		global subject
		subject = ""
	try:
		global year
		year = results['hits']['hits'][0]['_source']['article']['article-meta']['year'][0]
	except:
		global year
		year = ""
	try:
		global authors
		authors = []
		for i in range(0, len(results['hits']['hits'][0]['_source']['article']['article-meta']['contrib-group'][0]['contrib'])):
			authors.append(results['hits']['hits'][0]['_source']['article']['article-meta']['contrib-group'][0]['contrib'][i]['string-name'][0])
	except:
		global authors
		authors.append('')

def findWord(word):
    return re.compile(r'\b({0})\b'.format(word), flags=re.IGNORECASE).search


"""
This is the local directory where we store all the articles
including only the body of the text.
"""
rootdir = '/Users/matthewnunez/Desktop/working/notebooks/journals'

"""
These variables store n-gram counts and the metadata strings
that will be used to summarize the data cumulatively for each
journal and the corpus overall.
"""
corpusoutput = "metadata"
onegramcorpuscount = 0
twogramcorpuscount = 0
threegramcorpuscount = 0
fourgramcorpuscount = 0

twogramjournalcount = 0
threegramjournalcount = 0
fourgramjournalcount = 0

corpus1gramdict = dict()

corpus2gramspecdict = dict()
corpus2gramtypdict = dict()
corpus2gramspeciesdict = dict()
corpus2gramgendict = dict()
corpus2gramformdict = dict()
corpus2gramsubspeciesdict = dict()
corpus2gramecodict = dict()

corpus3gramspecdict = dict()
corpus3gramtypdict = dict()
corpus3gramspeciesdict = dict()
corpus3gramgendict = dict()
corpus3gramformdict = dict()
corpus3gramsubspeciesdict = dict()
corpus3gramecodict = dict()

corpus4gramspecdict = dict()
corpus4gramtypdict = dict()
corpus4gramspeciesdict = dict()
corpus4gramgendict = dict()
corpus4gramformdict = dict()
corpus4gramsubspeciesdict = dict()
corpus4gramecodict = dict()


"""
The first step is to walk through all the files and
retrieve the metadata, n-gram counts, and frequencies.
This is done through the use of the search function 
(for metadata) and analysis of the body of each text. 
These results are appended to the journal counts, corpus 
counts, and output strings.
"""
os.chdir(rootdir)
for subdir, dirs, files in os.walk(rootdir):
	journalcount = 0
	corpusarticlecount = 0
	for dir in dirs:
		journalonegramoutput = "metadata"
		journaltwogramoutput = "metadata"
		journalthreegramoutput = "metadata"
		journalfourgramoutput = "metadata"
		onegramjournalcount = 0
		journalcount += 1
		folder = dir
		os.chdir(os.path.join(subdir, dir))
		totaldict = dict()
		"""
		These variables will be appended with the article
		n-gram dictionaries to be a running aggregation of
		n-gram lists for all the articles in each journal.
		"""
		journal1gramdict = dict()
		
		journal2gramspecdict = dict()
		journal2gramtypdict = dict()
		journal2gramspeciesdict = dict()
		journal2gramgendict = dict()
		journal2gramformdict = dict()
		journal2gramsubspeciesdict = dict()
		journal2gramecodict = dict()

		journal3gramspecdict = dict()
		journal3gramtypdict = dict()
		journal3gramspeciesdict = dict()
		journal3gramgendict = dict()
		journal3gramformdict = dict()
		journal3gramsubspeciesdict = dict()
		journal3gramecodict = dict()

		journal4gramspecdict = dict()
		journal4gramtypdict = dict()
		journal4gramspeciesdict = dict()
		journal4gramgendict = dict()
		journal4gramformdict = dict()
		journal4gramsubspeciesdict = dict()
		journal4gramecodict = dict()

		articlecount = 0
		for file in os.listdir(os.getcwd()):
			if not file.startswith('.'):
				articlecount += 1
				corpusarticlecount += 1
				input = os.path.splitext(file)[0]
				if '_' in input:
					input = input.replace('_', '/')
				
				"""
				The following retrieves metadata for the article using the 
				search function and appends to the output string.
				"""
				search('http://amphora.asu.edu:9200/a_jstor*/_search?&pretty', input)
				articleoutput = "metadata\n\tTitle:\t\t" + title + "\n\tSubject:\t" + subject + "\n\tJournal:\t" + journal + "\n\tAuthor/s:"
				for i in range(0, len(authors)):
					articleoutput += "\n\t\t\t" + authors[i]
				articleoutput += "\n\tYear:\t\t" + year + "\n\tDOI:\t\t" + doi
				
				filename = os.path.splitext(file)[0] + '.txt'
				os.chdir('/Users/matthewnunez/Desktop/working/notebooks/journals/' + dir)
				with open(file, 'r') as readfile:
					singlewordstring = readfile.read()
					
					"""
					The following retrieves 1-grams, counts, and frequencies.
					It also adds them to the output string and appends them 
					to the journal and corpus dictionaries.
					"""
					count = 0
					output = {}
					inputstring = singlewordstring.lower()
					inputstring.encode('utf-8')
					inputstring = re.compile(r'[^a-zA-Z]+', re.UNICODE).split(inputstring)
					n = 1
					found = 0
					for i in range(len(inputstring)):
						if inputstring[i] == '':
							found += 1
					for i in range(found):
							inputstring.remove('')
					for i in range(len(inputstring)-n+1):
						g = ' '.join(inputstring[i:i+n])
						output.setdefault(g, 0)
						output[g] += 1
					count = sum(output.values())
					tempdict = Counter(output)
					output = Counter(output)
					output = output.most_common()
					journal1gramdict = Counter(journal1gramdict)
					journal1gramdict = tempdict + journal1gramdict
					journal1gramdict = dict(journal1gramdict)
					articleoutput += "\n1-grams:\n\tcount: " + str(count) + "\n\tlist:"
					output = OrderedDict(output)
					for key in output:
						articleoutput += "\n\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(output[key]), 'freq: ' + str(log10(float(output[key])/float(count))))
					onegramjournalcount += count

					"""
					The following retrieves 2-grams, counts, and frequencies.
					It also adds them to the output string and appends them 
					to the journal and corpus dictionaries.
					"""
					count = 0
					output = {}
					inputstring = singlewordstring.lower()
					inputstring = re.compile(r'[^a-zA-Z]+', re.UNICODE).split(inputstring)
					n = 2
					for i in range(len(inputstring)-n+1):
						g = ' '.join(inputstring[i:i+n])
						output.setdefault(g, 0)
						output[g] += 1
					count = sum(output.values())

					"""
					The following removes 2-grams from the dictionary that 
					do not contain words on the approved list.
					"""
					deletelist = []
					for key in list(output):
						found = False
						for word in ngramwordlist:
							if key.find(word)>-1:
								found = True
								break
							else:
								found = False
						if found == False:
							if not key in deletelist:
								deletelist.append(key)
					for key in output.keys():
						if key in deletelist:
							del output[key]
							
					"""
					The following combines counts of 2-grams that are common 
					across sublists of the ngramwordlist.
					"""

					"""
					specimen, specimens
					"""
					specoutput = {}
					specimenoutput = {}
					specimensoutput = {}
					
					for key in list(output):
						if findWord('specimen')(key):
							newkey = key.replace('specimen','x')
							specimenoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('specimens')(key):
							newkey = key.replace('specimens','x')
							specimensoutput[newkey] = output[key]
							output.pop(key, None)

					specimenoutput = Counter(specimenoutput)
					specimensoutput = Counter(specimensoutput)
					specoutput = specimenoutput + specimensoutput

					journal2gramspecdict = Counter(journal2gramspecdict)
					journal2gramspecdict = specoutput + journal2gramspecdict
					journal2gramspecdict.most_common()
					articleoutput += "\n2-grams:\n\tcount: " + str(count) + "\n\tlist:" + "\n\t\tspecimen, specimens:"
					specoutput = specoutput.most_common()
					specoutput = OrderedDict(specoutput)
					for key in specoutput:
						articleoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(specoutput[key]), 'freq: ' + str(log10(float(specoutput[key])/float(count))))
					twogramjournalcount += count

					"""
					type, types, typical, typify, typifies, typifying
					"""
					typoutput = {}
					typeoutput = {}
					typesoutput = {}
					typicaloutput = {}
					typifyoutput = {}
					typifiesoutput = {}
					typifyingoutput = {}
					
					for key in list(output):
						if findWord('type')(key):
							newkey = key.replace('type','x')
							typeoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('types')(key):
							newkey = key.replace('types','x')
							typesoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('typical')(key):
							newkey = key.replace('typical','x')
							typicaloutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('typify')(key):
							newkey = key.replace('typify','x')
							typifyoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('typifies')(key):
							newkey = key.replace('typifies','x')
							typifiesoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('typifying')(key):
							newkey = key.replace('typifying','x')
							typifyingoutput[newkey] = output[key]
							output.pop(key, None)

					typeoutput = Counter(typeoutput)
					typesoutput = Counter(typesoutput)
					typicaloutput = Counter(typicaloutput)
					typifyoutput = Counter(typifyoutput)
					typifiesoutput = Counter(typifiesoutput)
					typifyingoutput = Counter(typifyingoutput)
					typoutput = typeoutput + typesoutput + typicaloutput + typifyoutput + typifiesoutput + typifyingoutput

					journal2gramtypdict = Counter(journal2gramtypdict)
					journal2gramtypdict = typoutput + journal2gramtypdict
					journal2gramtypdict.most_common()
					articleoutput += "\n\t\ttype, types, typical, typify, typifies, typifying:"
					typoutput = typoutput.most_common()
					typoutput = OrderedDict(typoutput)
					for key in typoutput:
						articleoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(typoutput[key]), 'freq: ' + str(log10(float(typoutput[key])/float(count))))

					"""
					species
					"""
					speciesoutput = {}
					
					for key in list(output):
						if findWord('species')(key):
							newkey = key.replace('species','x')
							speciesoutput[newkey] = output[key]
							output.pop(key, None)

					speciesoutput = Counter(speciesoutput)

					journal2gramspeciesdict = Counter(journal2gramspeciesdict)
					journal2gramspeciesdict = speciesoutput + journal2gramspeciesdict
					journal2gramspeciesdict.most_common()
					articleoutput += "\n\t\tspecies:"
					speciesoutput = speciesoutput.most_common()
					speciesoutput = OrderedDict(speciesoutput)
					for key in speciesoutput:
						articleoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(speciesoutput[key]), 'freq: ' + str(log10(float(speciesoutput[key])/float(count))))

					"""
					genus, genera
					"""
					genoutput = {}
					genusoutput = {}
					generaoutput = {}
					
					for key in list(output):
						if findWord('genus')(key):
							newkey = key.replace('genus','x')
							genusoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('genera')(key):
							newkey = key.replace('genera','x')
							generaoutput[newkey] = output[key]
							output.pop(key, None)

					genusoutput = Counter(genusoutput)
					generaoutput = Counter(generaoutput)
					genoutput = genusoutput + generaoutput

					journal2gramgendict = Counter(journal2gramgendict)
					journal2gramgendict = genoutput + journal2gramgendict
					journal2gramgendict.most_common()
					articleoutput += "\n\t\tgenus, genera:"
					genoutput = genoutput.most_common()
					genoutput = OrderedDict(genoutput)
					for key in genoutput:
						articleoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(genoutput[key]), 'freq: ' + str(log10(float(genoutput[key])/float(count))))

					"""
					form
					"""
					formoutput = {}
					
					for key in list(output):
						if findWord('form')(key):
							newkey = key.replace('form','x')
							formoutput[newkey] = output[key]
							output.pop(key, None)

					formoutput = Counter(formoutput)

					journal2gramformdict = Counter(journal2gramformdict)
					journal2gramformdict = formoutput + journal2gramformdict
					journal2gramformdict.most_common()
					articleoutput += "\n\t\tform:"
					formoutput = formoutput.most_common()
					formoutput = OrderedDict(formoutput)
					for key in formoutput:
						articleoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(formoutput[key]), 'freq: ' + str(log10(float(formoutput[key])/float(count))))

					"""
					subspecies
					"""
					subspeciesoutput = {}
					
					for key in list(output):
						if findWord('subspecies')(key):
							newkey = key.replace('subspecies','x')
							subspeciesoutput[newkey] = output[key]
							output.pop(key, None)

					subspeciesoutput = Counter(subspeciesoutput)

					journal2gramsubspeciesdict = Counter(journal2gramsubspeciesdict)
					journal2gramsubspeciesdict = subspeciesoutput + journal2gramsubspeciesdict
					journal2gramsubspeciesdict.most_common()
					articleoutput += "\n\t\tsubspecies:"
					subspeciesoutput = subspeciesoutput.most_common()
					subspeciesoutput = OrderedDict(subspeciesoutput)
					for key in subspeciesoutput:
						articleoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(subspeciesoutput[key]), 'freq: ' + str(log10(float(subspeciesoutput[key])/float(count))))

					"""
					ecotype, ecotypes
					"""
					ecooutput = {}
					ecotypeoutput = {}
					ecotypesoutput = {}
					
					for key in list(output):
						if findWord('ecotype')(key):
							newkey = key.replace('ecotype','x')
							ecotypeoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('ecotypes')(key):
							newkey = key.replace('ecotypes','x')
							ecotypesoutput[newkey] = output[key]
							output.pop(key, None)

					ecotypeoutput = Counter(ecotypeoutput)
					ecotypesoutput = Counter(ecotypesoutput)
					ecooutput = ecotypeoutput + ecotypesoutput

					journal2gramecodict = Counter(journal2gramecodict)
					journal2gramecodict = ecooutput + journal2gramecodict
					journal2gramecodict.most_common()
					articleoutput += "\n\t\tecotype, ecotypes:"
					ecooutput = ecooutput.most_common()
					ecooutput = OrderedDict(ecooutput)
					for key in ecooutput:
						articleoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(ecooutput[key]), 'freq: ' + str(log10(float(ecooutput[key])/float(count))))

					"""
					The following retrieves 3-grams, counts, and frequencies.
					It also adds them to the output string and appends them 
					to the journal and corpus dictionaries. It also removes 
					3-grams from the dictionary that do not contain words on 
					the approved list.
					"""
					count = 0
					output = {}
					inputstring = singlewordstring.lower()
					inputstring = re.compile(r'[^a-zA-Z]+', re.UNICODE).split(inputstring)
					n = 3
					for i in range(len(inputstring)-n+1):
						g = ' '.join(inputstring[i:i+n])
						output.setdefault(g, 0)
						output[g] += 1
					count = sum(output.values())
					deletelist = []
					for key in list(output):
						found = False
						for word in ngramwordlist:
							if key.find(word)>-1:
								found = True
								break
							else:
								found = False
						if found == False:
							if not key in deletelist:
								deletelist.append(key)
					for key in output.keys():
						if key in deletelist:
							del output[key]

					"""
					The following combines counts of 3-grams that are common 
					across sublists of the ngramwordlist.
					"""

					"""
					specimen, specimens
					"""
					specoutput = {}
					specimenoutput = {}
					specimensoutput = {}
					
					for key in list(output):
						if findWord('specimen')(key):
							newkey = key.replace('specimen','x')
							specimenoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('specimens')(key):
							newkey = key.replace('specimens','x')
							specimensoutput[newkey] = output[key]
							output.pop(key, None)

					specimenoutput = Counter(specimenoutput)
					specimensoutput = Counter(specimensoutput)
					specoutput = specimenoutput + specimensoutput

					journal3gramspecdict = Counter(journal3gramspecdict)
					journal3gramspecdict = specoutput + journal3gramspecdict
					journal3gramspecdict.most_common()
					articleoutput += "\n3-grams:\n\tcount: " + str(count) + "\n\tlist:" + "\n\t\tspecimen, specimens:"
					specoutput = specoutput.most_common()
					specoutput = OrderedDict(specoutput)
					for key in specoutput:
						articleoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(specoutput[key]), 'freq: ' + str(log10(float(specoutput[key])/float(count))))
					threegramjournalcount += count

					"""
					type, types, typical, typify, typifies, typifying
					"""
					typoutput = {}
					typeoutput = {}
					typesoutput = {}
					typicaloutput = {}
					typifyoutput = {}
					typifiesoutput = {}
					typifyingoutput = {}
					
					for key in list(output):
						if findWord('type')(key):
							newkey = key.replace('type','x')
							typeoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('types')(key):
							newkey = key.replace('types','x')
							typesoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('typical')(key):
							newkey = key.replace('typical','x')
							typicaloutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('typify')(key):
							newkey = key.replace('typify','x')
							typifyoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('typifies')(key):
							newkey = key.replace('typifies','x')
							typifiesoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('typifying')(key):
							newkey = key.replace('typifying','x')
							typifyingoutput[newkey] = output[key]
							output.pop(key, None)

					typeoutput = Counter(typeoutput)
					typesoutput = Counter(typesoutput)
					typicaloutput = Counter(typicaloutput)
					typifyoutput = Counter(typifyoutput)
					typifiesoutput = Counter(typifiesoutput)
					typifyingoutput = Counter(typifyingoutput)
					typoutput = typeoutput + typesoutput + typicaloutput + typifyoutput + typifiesoutput + typifyingoutput

					journal3gramtypdict = Counter(journal3gramtypdict)
					journal3gramtypdict = typoutput + journal3gramtypdict
					journal3gramtypdict.most_common()
					articleoutput += "\n\t\ttype, types, typical, typify, typifies, typifying:"
					typoutput = typoutput.most_common()
					typoutput = OrderedDict(typoutput)
					for key in typoutput:
						articleoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(typoutput[key]), 'freq: ' + str(log10(float(typoutput[key])/float(count))))

					"""
					species
					"""
					speciesoutput = {}
					
					for key in list(output):
						if findWord('species')(key):
							newkey = key.replace('species','x')
							speciesoutput[newkey] = output[key]
							output.pop(key, None)

					speciesoutput = Counter(speciesoutput)

					journal3gramspeciesdict = Counter(journal3gramspeciesdict)
					journal3gramspeciesdict = speciesoutput + journal3gramspeciesdict
					journal3gramspeciesdict.most_common()
					articleoutput += "\n\t\tspecies:"
					speciesoutput = speciesoutput.most_common()
					speciesoutput = OrderedDict(speciesoutput)
					for key in speciesoutput:
						articleoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(speciesoutput[key]), 'freq: ' + str(log10(float(speciesoutput[key])/float(count))))

					"""
					genus, genera
					"""
					genoutput = {}
					genusoutput = {}
					generaoutput = {}
					
					for key in list(output):
						if findWord('genus')(key):
							newkey = key.replace('genus','x')
							genusoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('genera')(key):
							newkey = key.replace('genera','x')
							generaoutput[newkey] = output[key]
							output.pop(key, None)

					genusoutput = Counter(genusoutput)
					generaoutput = Counter(generaoutput)
					genoutput = genusoutput + generaoutput

					journal3gramgendict = Counter(journal3gramgendict)
					journal3gramgendict = genoutput + journal3gramgendict
					journal3gramgendict.most_common()
					articleoutput += "\n\t\tgenus, genera:"
					genoutput = genoutput.most_common()
					genoutput = OrderedDict(genoutput)
					for key in genoutput:
						articleoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(genoutput[key]), 'freq: ' + str(log10(float(genoutput[key])/float(count))))

					"""
					form
					"""
					formoutput = {}
					
					for key in list(output):
						if findWord('form')(key):
							newkey = key.replace('form','x')
							formoutput[newkey] = output[key]
							output.pop(key, None)

					formoutput = Counter(formoutput)

					journal3gramformdict = Counter(journal3gramformdict)
					journal3gramformdict = formoutput + journal3gramformdict
					journal3gramformdict.most_common()
					articleoutput += "\n\t\tform:"
					formoutput = formoutput.most_common()
					formoutput = OrderedDict(formoutput)
					for key in formoutput:
						articleoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(formoutput[key]), 'freq: ' + str(log10(float(formoutput[key])/float(count))))

					"""
					subspecies
					"""
					subspeciesoutput = {}
					
					for key in list(output):
						if findWord('subspecies')(key):
							newkey = key.replace('subspecies','x')
							subspeciesoutput[newkey] = output[key]
							output.pop(key, None)

					subspeciesoutput = Counter(subspeciesoutput)

					journal3gramsubspeciesdict = Counter(journal3gramsubspeciesdict)
					journal3gramsubspeciesdict = subspeciesoutput + journal3gramsubspeciesdict
					journal3gramsubspeciesdict.most_common()
					articleoutput += "\n\t\tsubspecies:"
					subspeciesoutput = subspeciesoutput.most_common()
					subspeciesoutput = OrderedDict(subspeciesoutput)
					for key in subspeciesoutput:
						articleoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(subspeciesoutput[key]), 'freq: ' + str(log10(float(subspeciesoutput[key])/float(count))))

					"""
					ecotype, ecotypes
					"""
					ecooutput = {}
					ecotypeoutput = {}
					ecotypesoutput = {}
					
					for key in list(output):
						if findWord('ecotype')(key):
							newkey = key.replace('ecotype','x')
							ecotypeoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('ecotypes')(key):
							newkey = key.replace('ecotypes','x')
							ecotypesoutput[newkey] = output[key]
							output.pop(key, None)

					ecotypeoutput = Counter(ecotypeoutput)
					ecotypesoutput = Counter(ecotypesoutput)
					ecooutput = ecotypeoutput + ecotypesoutput

					journal3gramecodict = Counter(journal3gramecodict)
					journal3gramecodict = ecooutput + journal3gramecodict
					journal3gramecodict.most_common()
					articleoutput += "\n\t\tecotype, ecotypes:"
					ecooutput = ecooutput.most_common()
					ecooutput = OrderedDict(ecooutput)
					for key in ecooutput:
						articleoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(ecooutput[key]), 'freq: ' + str(log10(float(ecooutput[key])/float(count))))

					"""
					The following retrieves 4-grams, counts, and frequencies.
					It also adds them to the output string and appends them 
					to the journal and corpus dictionaries. It also removes 
					4-grams from the dictionary that do not contain words on 
					the approved list.
					"""
					count = 0
					output = {}
					inputstring = singlewordstring.lower()
					inputstring = re.compile(r'[^a-zA-Z]+', re.UNICODE).split(inputstring)
					n = 4
					for i in range(len(inputstring)-n+1):
						g = ' '.join(inputstring[i:i+n])
						output.setdefault(g, 0)
						output[g] += 1
					count = sum(output.values())
					deletelist = []
					for key in list(output):
						found = False
						for word in ngramwordlist:
							if key.find(word)>-1:
								found = True
								break
							else:
								found = False
						if found == False:
							if not key in deletelist:
								deletelist.append(key)
					for key in output.keys():
						if key in deletelist:
							del output[key]

					"""
					The following combines counts of 4-grams that are common 
					across sublists of the ngramwordlist.
					"""

					"""
					specimen, specimens
					"""
					specoutput = {}
					specimenoutput = {}
					specimensoutput = {}
					
					for key in list(output):
						if findWord('specimen')(key):
							newkey = key.replace('specimen','x')
							specimenoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('specimens')(key):
							newkey = key.replace('specimens','x')
							specimensoutput[newkey] = output[key]
							output.pop(key, None)

					specimenoutput = Counter(specimenoutput)
					specimensoutput = Counter(specimensoutput)
					specoutput = specimenoutput + specimensoutput

					journal4gramspecdict = Counter(journal4gramspecdict)
					journal4gramspecdict = specoutput + journal4gramspecdict
					journal4gramspecdict.most_common()
					articleoutput += "\n4-grams:\n\tcount: " + str(count) + "\n\tlist:" + "\n\t\tspecimen, specimens:"
					specoutput = specoutput.most_common()
					specoutput = OrderedDict(specoutput)
					for key in specoutput:
						articleoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(specoutput[key]), 'freq: ' + str(log10(float(specoutput[key])/float(count))))
					fourgramjournalcount += count

					"""
					type, types, typical, typify, typifies, typifying
					"""
					typoutput = {}
					typeoutput = {}
					typesoutput = {}
					typicaloutput = {}
					typifyoutput = {}
					typifiesoutput = {}
					typifyingoutput = {}
					
					for key in list(output):
						if findWord('type')(key):
							newkey = key.replace('type','x')
							typeoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('types')(key):
							newkey = key.replace('types','x')
							typesoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('typical')(key):
							newkey = key.replace('typical','x')
							typicaloutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('typify')(key):
							newkey = key.replace('typify','x')
							typifyoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('typifies')(key):
							newkey = key.replace('typifies','x')
							typifiesoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('typifying')(key):
							newkey = key.replace('typifying','x')
							typifyingoutput[newkey] = output[key]
							output.pop(key, None)

					typeoutput = Counter(typeoutput)
					typesoutput = Counter(typesoutput)
					typicaloutput = Counter(typicaloutput)
					typifyoutput = Counter(typifyoutput)
					typifiesoutput = Counter(typifiesoutput)
					typifyingoutput = Counter(typifyingoutput)
					typoutput = typeoutput + typesoutput + typicaloutput + typifyoutput + typifiesoutput + typifyingoutput

					journal4gramtypdict = Counter(journal4gramtypdict)
					journal4gramtypdict = typoutput + journal4gramtypdict
					journal4gramtypdict.most_common()
					articleoutput += "\n\t\ttype, types, typical, typify, typifies, typifying:"
					typoutput = typoutput.most_common()
					typoutput = OrderedDict(typoutput)
					for key in typoutput:
						articleoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(typoutput[key]), 'freq: ' + str(log10(float(typoutput[key])/float(count))))

					"""
					species
					"""
					speciesoutput = {}
					
					for key in list(output):
						if findWord('species')(key):
							newkey = key.replace('species','x')
							speciesoutput[newkey] = output[key]
							output.pop(key, None)

					speciesoutput = Counter(speciesoutput)

					journal4gramspeciesdict = Counter(journal4gramspeciesdict)
					journal4gramspeciesdict = speciesoutput + journal4gramspeciesdict
					journal4gramspeciesdict.most_common()
					articleoutput += "\n\t\tspecies:"
					speciesoutput = speciesoutput.most_common()
					speciesoutput = OrderedDict(speciesoutput)
					for key in speciesoutput:
						articleoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(speciesoutput[key]), 'freq: ' + str(log10(float(speciesoutput[key])/float(count))))

					"""
					genus, genera
					"""
					genoutput = {}
					genusoutput = {}
					generaoutput = {}
					
					for key in list(output):
						if findWord('genus')(key):
							newkey = key.replace('genus','x')
							genusoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('genera')(key):
							newkey = key.replace('genera','x')
							generaoutput[newkey] = output[key]
							output.pop(key, None)

					genusoutput = Counter(genusoutput)
					generaoutput = Counter(generaoutput)
					genoutput = genusoutput + generaoutput

					journal4gramgendict = Counter(journal4gramgendict)
					journal4gramgendict = genoutput + journal4gramgendict
					journal4gramgendict.most_common()
					articleoutput += "\n\t\tgenus, genera:"
					genoutput = genoutput.most_common()
					genoutput = OrderedDict(genoutput)
					for key in genoutput:
						articleoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(genoutput[key]), 'freq: ' + str(log10(float(genoutput[key])/float(count))))

					"""
					form
					"""
					formoutput = {}
					
					for key in list(output):
						if findWord('form')(key):
							newkey = key.replace('form','x')
							formoutput[newkey] = output[key]
							output.pop(key, None)

					formoutput = Counter(formoutput)

					journal4gramformdict = Counter(journal4gramformdict)
					journal4gramformdict = formoutput + journal4gramformdict
					journal4gramformdict.most_common()
					articleoutput += "\n\t\tform:"
					formoutput = formoutput.most_common()
					formoutput = OrderedDict(formoutput)
					for key in formoutput:
						articleoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(formoutput[key]), 'freq: ' + str(log10(float(formoutput[key])/float(count))))

					"""
					subspecies
					"""
					subspeciesoutput = {}
					
					for key in list(output):
						if findWord('subspecies')(key):
							newkey = key.replace('subspecies','x')
							subspeciesoutput[newkey] = output[key]
							output.pop(key, None)

					subspeciesoutput = Counter(subspeciesoutput)

					journal4gramsubspeciesdict = Counter(journal4gramsubspeciesdict)
					journal4gramsubspeciesdict = subspeciesoutput + journal4gramsubspeciesdict
					journal4gramsubspeciesdict.most_common()
					articleoutput += "\n\t\tsubspecies:"
					subspeciesoutput = subspeciesoutput.most_common()
					subspeciesoutput = OrderedDict(subspeciesoutput)
					for key in subspeciesoutput:
						articleoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(subspeciesoutput[key]), 'freq: ' + str(log10(float(subspeciesoutput[key])/float(count))))

					"""
					ecotype, ecotypes
					"""
					ecooutput = {}
					ecotypeoutput = {}
					ecotypesoutput = {}
					
					for key in list(output):
						if findWord('ecotype')(key):
							newkey = key.replace('ecotype','x')
							ecotypeoutput[newkey] = output[key]
							output.pop(key, None)

					for key in list(output):
						if findWord('ecotypes')(key):
							newkey = key.replace('ecotypes','x')
							ecotypesoutput[newkey] = output[key]
							output.pop(key, None)

					ecotypeoutput = Counter(ecotypeoutput)
					ecotypesoutput = Counter(ecotypesoutput)
					ecooutput = ecotypeoutput + ecotypesoutput

					journal4gramecodict = Counter(journal4gramecodict)
					journal4gramecodict = ecooutput + journal4gramecodict
					journal4gramecodict.most_common()
					articleoutput += "\n\t\tecotype, ecotypes:"
					ecooutput = ecooutput.most_common()
					ecooutput = OrderedDict(ecooutput)
					for key in ecooutput:
						articleoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(ecooutput[key]), 'freq: ' + str(log10(float(ecooutput[key])/float(count))))

				"""
				The following creates a folder in the results directory, unless
				it already exists, for the given journal and adds the analysis 
				output for the given article to that folder.
				"""
				os.chdir('/Users/matthewnunez/Desktop/working/notebooks/results/')
				if not os.path.exists(folder):
					os.mkdir(folder)
				os.chdir(folder)
				articleoutput.encode('utf-8')
				with open(filename, 'w') as f:
					f.write(articleoutput.encode('utf8'))

		"""
		The following takes the running journal dictionary, to which
		each article has been appended, and adds it to the output string
		for the given journal. This first block is for 1-grams.
		"""
		tempdict = Counter(journal1gramdict)
		journal1gramdict = Counter(journal1gramdict)
		journal1gramdict = journal1gramdict.most_common()
		corpus1gramdict = Counter(corpus1gramdict)
		corpus1gramdict = tempdict + corpus1gramdict
		corpus1gramdict = dict(corpus1gramdict)
		journalonegramoutput += "\n\tJournal:\t" + dir + "\n\tArticle Count:\t" + str(articlecount) + "\n1-grams:\n\tcount: " + str(onegramjournalcount) + "\n\tlist:"
		journal1gramdict = OrderedDict(journal1gramdict)
		for key in journal1gramdict:
			journalonegramoutput += "\n\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(journal1gramdict[key]), 'freq: ' + str(log10(float(journal1gramdict[key])/float(onegramjournalcount))))
		onegramcorpuscount += onegramjournalcount

		"""
		2-grams
		"""
		corpus2gramspecdict = Counter(corpus2gramspecdict)
		corpus2gramtypdict = Counter(corpus2gramtypdict)
		corpus2gramspeciesdict = Counter(corpus2gramspeciesdict)
		corpus2gramgendict = Counter(corpus2gramgendict)
		corpus2gramformdict = Counter(corpus2gramformdict)
		corpus2gramsubspeciesdict = Counter(corpus2gramsubspeciesdict)
		corpus2gramecodict = Counter(corpus2gramecodict)

		corpus2gramspecdict = journal2gramspecdict + corpus2gramspecdict
		corpus2gramtypdict = journal2gramtypdict + corpus2gramtypdict
		corpus2gramspeciesdict = journal2gramspeciesdict + corpus2gramspeciesdict
		corpus2gramgendict = journal2gramgendict + corpus2gramgendict
		corpus2gramformdict = journal2gramformdict + corpus2gramformdict
		corpus2gramsubspeciesdict = journal2gramsubspeciesdict + corpus2gramsubspeciesdict
		corpus2gramecodict = journal2gramecodict + corpus2gramecodict

		corpus2gramspecdict.most_common()
		corpus2gramtypdict.most_common()
		corpus2gramspeciesdict.most_common()
		corpus2gramgendict.most_common()
		corpus2gramformdict.most_common()
		corpus2gramsubspeciesdict.most_common()
		corpus2gramecodict.most_common()

		journaltwogramoutput += "\n\tJournal:\t" + dir + "\n\tArticle Count:\t" + str(articlecount) + "\n2-grams:\n\tcount: " + str(twogramjournalcount) + "\n\tlist:" + "\n\t\tspecimen, specimens:"
		journal2gramspecdict = journal2gramspecdict.most_common()
		journal2gramspecdict = OrderedDict(journal2gramspecdict)
		for key in journal2gramspecdict:
			journaltwogramoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(journal2gramspecdict[key]), 'freq: ' + str(log10(float(journal2gramspecdict[key])/float(twogramjournalcount))))
		twogramcorpuscount += twogramjournalcount

		journaltwogramoutput += "\n\t\ttype, types, typical, typify, typifies, typifying:"
		journal2gramtypdict = journal2gramtypdict.most_common()
		journal2gramtypdict = OrderedDict(journal2gramtypdict)
		for key in journal2gramtypdict:
			journaltwogramoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(journal2gramtypdict[key]), 'freq: ' + str(log10(float(journal2gramtypdict[key])/float(twogramjournalcount))))

		journaltwogramoutput += "\n\t\tspecies:"
		journal2gramspeciesdict = journal2gramspeciesdict.most_common()
		journal2gramspeciesdict = OrderedDict(journal2gramspeciesdict)
		for key in journal2gramspeciesdict:
			journaltwogramoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(journal2gramspeciesdict[key]), 'freq: ' + str(log10(float(journal2gramspeciesdict[key])/float(twogramjournalcount))))

		journaltwogramoutput += "\n\t\tgenus, genera:"
		journal2gramgendict = journal2gramgendict.most_common()
		journal2gramgendict = OrderedDict(journal2gramgendict)
		for key in journal2gramgendict:
			journaltwogramoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(journal2gramgendict[key]), 'freq: ' + str(log10(float(journal2gramgendict[key])/float(twogramjournalcount))))

		journaltwogramoutput += "\n\t\tform:"
		journal2gramformdict = journal2gramformdict.most_common()
		journal2gramformdict = OrderedDict(journal2gramformdict)
		for key in journal2gramformdict:
			journaltwogramoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(journal2gramformdict[key]), 'freq: ' + str(log10(float(journal2gramformdict[key])/float(twogramjournalcount))))

		journaltwogramoutput += "\n\t\tsubspecies:"
		journal2gramsubspeciesdict = journal2gramsubspeciesdict.most_common()
		journal2gramsubspeciesdict = OrderedDict(journal2gramsubspeciesdict)
		for key in journal2gramsubspeciesdict:
			journaltwogramoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(journal2gramsubspeciesdict[key]), 'freq: ' + str(log10(float(journal2gramsubspeciesdict[key])/float(twogramjournalcount))))

		journaltwogramoutput += "\n\t\tecotype, ecotypes:"
		journal2gramecodict = journal2gramecodict.most_common()
		journal2gramecodict = OrderedDict(journal2gramecodict)
		for key in journal2gramecodict:
			journaltwogramoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(journal2gramecodict[key]), 'freq: ' + str(log10(float(journal2gramecodict[key])/float(twogramjournalcount))))


		"""
		3-grams
		"""
		corpus3gramspecdict = Counter(corpus3gramspecdict)
		corpus3gramtypdict = Counter(corpus3gramtypdict)
		corpus3gramspeciesdict = Counter(corpus3gramspeciesdict)
		corpus3gramgendict = Counter(corpus3gramgendict)
		corpus3gramformdict = Counter(corpus3gramformdict)
		corpus3gramsubspeciesdict = Counter(corpus3gramsubspeciesdict)
		corpus3gramecodict = Counter(corpus3gramecodict)

		corpus3gramspecdict = journal3gramspecdict + corpus3gramspecdict
		corpus3gramtypdict = journal3gramtypdict + corpus3gramtypdict
		corpus3gramspeciesdict = journal3gramspeciesdict + corpus3gramspeciesdict
		corpus3gramgendict = journal3gramgendict + corpus3gramgendict
		corpus3gramformdict = journal3gramformdict + corpus3gramformdict
		corpus3gramsubspeciesdict = journal3gramsubspeciesdict + corpus3gramsubspeciesdict
		corpus3gramecodict = journal3gramecodict + corpus3gramecodict

		corpus3gramspecdict.most_common()
		corpus3gramtypdict.most_common()
		corpus3gramspeciesdict.most_common()
		corpus3gramgendict.most_common()
		corpus3gramformdict.most_common()
		corpus3gramsubspeciesdict.most_common()
		corpus3gramecodict.most_common()

		journalthreegramoutput += "\n\tJournal:\t" + dir + "\n\tArticle Count:\t" + str(articlecount) + "\n3-grams:\n\tcount: " + str(threegramjournalcount) + "\n\tlist:" + "\n\t\tspecimen, specimens:"
		journal3gramspecdict = journal3gramspecdict.most_common()
		journal3gramspecdict = OrderedDict(journal3gramspecdict)
		for key in journal3gramspecdict:
			journalthreegramoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(journal3gramspecdict[key]), 'freq: ' + str(log10(float(journal3gramspecdict[key])/float(threegramjournalcount))))
		threegramcorpuscount += threegramjournalcount

		journalthreegramoutput += "\n\t\ttype, types, typical, typify, typifies, typifying:"
		journal3gramtypdict = journal3gramtypdict.most_common()
		journal3gramtypdict = OrderedDict(journal3gramtypdict)
		for key in journal3gramtypdict:
			journalthreegramoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(journal3gramtypdict[key]), 'freq: ' + str(log10(float(journal3gramtypdict[key])/float(threegramjournalcount))))

		journalthreegramoutput += "\n\t\tspecies:"
		journal3gramspeciesdict = journal3gramspeciesdict.most_common()
		journal3gramspeciesdict = OrderedDict(journal3gramspeciesdict)
		for key in journal3gramspeciesdict:
			journalthreegramoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(journal3gramspeciesdict[key]), 'freq: ' + str(log10(float(journal3gramspeciesdict[key])/float(threegramjournalcount))))

		journalthreegramoutput += "\n\t\tgenus, genera:"
		journal3gramgendict = journal3gramgendict.most_common()
		journal3gramgendict = OrderedDict(journal3gramgendict)
		for key in journal3gramgendict:
			journalthreegramoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(journal3gramgendict[key]), 'freq: ' + str(log10(float(journal3gramgendict[key])/float(threegramjournalcount))))

		journalthreegramoutput += "\n\t\tform:"
		journal3gramformdict = journal3gramformdict.most_common()
		journal3gramformdict = OrderedDict(journal3gramformdict)
		for key in journal3gramformdict:
			journalthreegramoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(journal3gramformdict[key]), 'freq: ' + str(log10(float(journal3gramformdict[key])/float(threegramjournalcount))))

		journalthreegramoutput += "\n\t\tsubspecies:"
		journal3gramsubspeciesdict = journal3gramsubspeciesdict.most_common()
		journal3gramsubspeciesdict = OrderedDict(journal3gramsubspeciesdict)
		for key in journal3gramsubspeciesdict:
			journalthreegramoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(journal3gramsubspeciesdict[key]), 'freq: ' + str(log10(float(journal3gramsubspeciesdict[key])/float(threegramjournalcount))))

		journalthreegramoutput += "\n\t\tecotype, ecotypes:"
		journal3gramecodict = journal3gramecodict.most_common()
		journal3gramecodict = OrderedDict(journal3gramecodict)
		for key in journal3gramecodict:
			journalthreegramoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(journal3gramecodict[key]), 'freq: ' + str(log10(float(journal3gramecodict[key])/float(threegramjournalcount))))

		"""
		4-grams
		"""
		corpus4gramspecdict = Counter(corpus4gramspecdict)
		corpus4gramtypdict = Counter(corpus4gramtypdict)
		corpus4gramspeciesdict = Counter(corpus4gramspeciesdict)
		corpus4gramgendict = Counter(corpus4gramgendict)
		corpus4gramformdict = Counter(corpus4gramformdict)
		corpus4gramsubspeciesdict = Counter(corpus4gramsubspeciesdict)
		corpus4gramecodict = Counter(corpus4gramecodict)

		corpus4gramspecdict = journal4gramspecdict + corpus4gramspecdict
		corpus4gramtypdict = journal4gramtypdict + corpus4gramtypdict
		corpus4gramspeciesdict = journal4gramspeciesdict + corpus4gramspeciesdict
		corpus4gramgendict = journal4gramgendict + corpus4gramgendict
		corpus4gramformdict = journal4gramformdict + corpus4gramformdict
		corpus4gramsubspeciesdict = journal4gramsubspeciesdict + corpus4gramsubspeciesdict
		corpus4gramecodict = journal4gramecodict + corpus4gramecodict

		corpus4gramspecdict.most_common()
		corpus4gramtypdict.most_common()
		corpus4gramspeciesdict.most_common()
		corpus4gramgendict.most_common()
		corpus4gramformdict.most_common()
		corpus4gramsubspeciesdict.most_common()
		corpus4gramecodict.most_common()

		journalfourgramoutput += "\n\tJournal:\t" + dir + "\n\tArticle Count:\t" + str(articlecount) + "\n4-grams:\n\tcount: " + str(fourgramjournalcount) + "\n\tlist:" + "\n\t\tspecimen, specimens:"
		journal4gramspecdict = journal4gramspecdict.most_common()
		journal4gramspecdict = OrderedDict(journal4gramspecdict)
		for key in journal4gramspecdict:
			journalfourgramoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(journal4gramspecdict[key]), 'freq: ' + str(log10(float(journal4gramspecdict[key])/float(fourgramjournalcount))))
		fourgramcorpuscount += fourgramjournalcount

		journalfourgramoutput += "\n\t\ttype, types, typical, typify, typifies, typifying:"
		journal4gramtypdict = journal4gramtypdict.most_common()
		journal4gramtypdict = OrderedDict(journal4gramtypdict)
		for key in journal4gramtypdict:
			journalfourgramoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(journal4gramtypdict[key]), 'freq: ' + str(log10(float(journal4gramtypdict[key])/float(fourgramjournalcount))))

		journalfourgramoutput += "\n\t\tspecies:"
		journal4gramspeciesdict = journal4gramspeciesdict.most_common()
		journal4gramspeciesdict = OrderedDict(journal4gramspeciesdict)
		for key in journal4gramspeciesdict:
			journalfourgramoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(journal4gramspeciesdict[key]), 'freq: ' + str(log10(float(journal4gramspeciesdict[key])/float(fourgramjournalcount))))

		journalfourgramoutput += "\n\t\tgenus, genera:"
		journal4gramgendict = journal4gramgendict.most_common()
		journal4gramgendict = OrderedDict(journal4gramgendict)
		for key in journal4gramgendict:
			journalfourgramoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(journal4gramgendict[key]), 'freq: ' + str(log10(float(journal4gramgendict[key])/float(fourgramjournalcount))))

		journalfourgramoutput += "\n\t\tform:"
		journal4gramformdict = journal4gramformdict.most_common()
		journal4gramformdict = OrderedDict(journal4gramformdict)
		for key in journal4gramformdict:
			journalfourgramoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(journal4gramformdict[key]), 'freq: ' + str(log10(float(journal4gramformdict[key])/float(fourgramjournalcount))))

		journalfourgramoutput += "\n\t\tsubspecies:"
		journal4gramsubspeciesdict = journal4gramsubspeciesdict.most_common()
		journal4gramsubspeciesdict = OrderedDict(journal4gramsubspeciesdict)
		for key in journal4gramsubspeciesdict:
			journalfourgramoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(journal4gramsubspeciesdict[key]), 'freq: ' + str(log10(float(journal4gramsubspeciesdict[key])/float(fourgramjournalcount))))

		journalfourgramoutput += "\n\t\tecotype, ecotypes:"
		journal4gramecodict = journal4gramecodict.most_common()
		journal4gramecodict = OrderedDict(journal4gramecodict)
		for key in journal4gramecodict:
			journalfourgramoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(journal4gramecodict[key]), 'freq: ' + str(log10(float(journal4gramecodict[key])/float(fourgramjournalcount))))

		"""
		The following writes the journal output string 
		to a file in the results directory.
		"""
		os.chdir('/Users/matthewnunez/Desktop/working/notebooks/results/')
		dirone = dir + ' one grams.txt'
		with open(dirone, 'w') as f:
			f.write(journalonegramoutput)
		os.chdir('/Users/matthewnunez/Desktop/working/notebooks/results/')
		dirtwo = dir + ' two grams.txt'
		with open(dirtwo, 'w') as f:
			f.write(journaltwogramoutput)
		os.chdir('/Users/matthewnunez/Desktop/working/notebooks/results/')
		dirthree = dir + ' three grams.txt'
		with open(dirthree, 'w') as f:
			f.write(journalthreegramoutput)
		os.chdir('/Users/matthewnunez/Desktop/working/notebooks/results/')
		dirfour = dir + ' four grams.txt'
		with open(dirfour, 'w') as f:
			f.write(journalfourgramoutput)

	"""
	The following takes the running corpus dictionary, to which
	each journal has been appended, and adds it to the output string.
	This first block is for 1-grams.
	"""
	corpus1gramdict = Counter(corpus1gramdict)
	corpus1gramdict = corpus1gramdict.most_common()
	corpusoutput += "\n\tJournal Count:\t" + str(journalcount) + "\n\tArticle Count:\t" + str(corpusarticlecount) + "\n1-grams:\n\tcount: " + str(onegramcorpuscount) + "\n\tlist:"
	corpus1gramdict = OrderedDict(corpus1gramdict)
	for key in corpus1gramdict:
		corpusoutput += "\n\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus1gramdict[key]), 'freq: ' + str(log10(float(corpus1gramdict[key])/float(onegramcorpuscount))))

	"""
	2-grams.
	"""
	corpusoutput += "\n2-grams:\n\tcount: " + str(twogramcorpuscount) + "\n\tlist:" + "\n\t\tspecimen, specimens:"
	corpus2gramspecdict = corpus2gramspecdict.most_common()
	corpus2gramspecdict = OrderedDict(corpus2gramspecdict)
	for key in corpus2gramspecdict:
		corpusoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus2gramspecdict[key]), 'freq: ' + str(log10(float(corpus2gramspecdict[key])/float(twogramcorpuscount))))

	corpusoutput += "\n\t\ttype, types, typical, typify, typifies, typifying:"
	corpus2gramtypdict = corpus2gramtypdict.most_common()
	corpus2gramtypdict = OrderedDict(corpus2gramtypdict)
	for key in corpus2gramtypdict:
		corpusoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus2gramtypdict[key]), 'freq: ' + str(log10(float(corpus2gramtypdict[key])/float(twogramcorpuscount))))

	corpusoutput += "\n\t\tspecies:"
	corpus2gramspeciesdict = corpus2gramspeciesdict.most_common()
	corpus2gramspeciesdict = OrderedDict(corpus2gramspeciesdict)
	for key in corpus2gramspeciesdict:
		corpusoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus2gramspeciesdict[key]), 'freq: ' + str(log10(float(corpus2gramspeciesdict[key])/float(twogramcorpuscount))))

	corpusoutput += "\n\t\tgenus, genera:"
	corpus2gramgendict = corpus2gramgendict.most_common()
	corpus2gramgendict = OrderedDict(corpus2gramgendict)
	for key in corpus2gramgendict:
		corpusoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus2gramgendict[key]), 'freq: ' + str(log10(float(corpus2gramgendict[key])/float(twogramcorpuscount))))

	corpusoutput += "\n\t\tform:"
	corpus2gramformdict = corpus2gramformdict.most_common()
	corpus2gramformdict = OrderedDict(corpus2gramformdict)
	for key in corpus2gramformdict:
		corpusoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus2gramformdict[key]), 'freq: ' + str(log10(float(corpus2gramformdict[key])/float(twogramcorpuscount))))

	corpusoutput += "\n\t\tsubspecies:"
	corpus2gramsubspeciesdict = corpus2gramsubspeciesdict.most_common()
	corpus2gramsubspeciesdict = OrderedDict(corpus2gramsubspeciesdict)
	for key in corpus2gramsubspeciesdict:
		corpusoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus2gramsubspeciesdict[key]), 'freq: ' + str(log10(float(corpus2gramsubspeciesdict[key])/float(twogramcorpuscount))))

	corpusoutput += "\n\t\tecotype, ecotypes:"
	corpus2gramecodict = corpus2gramecodict.most_common()
	corpus2gramecodict = OrderedDict(corpus2gramecodict)
	for key in corpus2gramecodict:
		corpusoutput += "\n\t\t\t" + '{:30s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus2gramecodict[key]), 'freq: ' + str(log10(float(corpus2gramecodict[key])/float(twogramcorpuscount))))

	"""
	3-grams.
	"""
	corpusoutput += "\n3-grams:\n\tcount: " + str(threegramcorpuscount) + "\n\tlist:" + "\n\t\tspecimen, specimens:"
	corpus3gramspecdict = corpus3gramspecdict.most_common()
	corpus3gramspecdict = OrderedDict(corpus3gramspecdict)
	for key in corpus3gramspecdict:
		corpusoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus3gramspecdict[key]), 'freq: ' + str(log10(float(corpus3gramspecdict[key])/float(threegramcorpuscount))))

	corpusoutput += "\n\t\ttype, types, typical, typify, typifies, typifying:"
	corpus3gramtypdict = corpus3gramtypdict.most_common()
	corpus3gramtypdict = OrderedDict(corpus3gramtypdict)
	for key in corpus3gramtypdict:
		corpusoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus3gramtypdict[key]), 'freq: ' + str(log10(float(corpus3gramtypdict[key])/float(threegramcorpuscount))))

	corpusoutput += "\n\t\tspecies:"
	corpus3gramspeciesdict = corpus3gramspeciesdict.most_common()
	corpus3gramspeciesdict = OrderedDict(corpus3gramspeciesdict)
	for key in corpus3gramspeciesdict:
		corpusoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus3gramspeciesdict[key]), 'freq: ' + str(log10(float(corpus3gramspeciesdict[key])/float(threegramcorpuscount))))

	corpusoutput += "\n\t\tgenus, genera:"
	corpus3gramgendict = corpus3gramgendict.most_common()
	corpus3gramgendict = OrderedDict(corpus3gramgendict)
	for key in corpus3gramgendict:
		corpusoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus3gramgendict[key]), 'freq: ' + str(log10(float(corpus3gramgendict[key])/float(threegramcorpuscount))))

	corpusoutput += "\n\t\tform:"
	corpus3gramformdict = corpus3gramformdict.most_common()
	corpus3gramformdict = OrderedDict(corpus3gramformdict)
	for key in corpus3gramformdict:
		corpusoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus3gramformdict[key]), 'freq: ' + str(log10(float(corpus3gramformdict[key])/float(threegramcorpuscount))))

	corpusoutput += "\n\t\tsubspecies:"
	corpus3gramsubspeciesdict = corpus3gramsubspeciesdict.most_common()
	corpus3gramsubspeciesdict = OrderedDict(corpus3gramsubspeciesdict)
	for key in corpus3gramsubspeciesdict:
		corpusoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus3gramsubspeciesdict[key]), 'freq: ' + str(log10(float(corpus3gramsubspeciesdict[key])/float(threegramcorpuscount))))

	corpusoutput += "\n\t\tecotype, ecotypes:"
	corpus3gramecodict = corpus3gramecodict.most_common()
	corpus3gramecodict = OrderedDict(corpus3gramecodict)
	for key in corpus3gramecodict:
		corpusoutput += "\n\t\t\t" + '{:40s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus3gramecodict[key]), 'freq: ' + str(log10(float(corpus3gramecodict[key])/float(threegramcorpuscount))))

	"""
	4-grams.
	"""
	corpusoutput += "\n4-grams:\n\tcount: " + str(fourgramcorpuscount) + "\n\tlist:" + "\n\t\tspecimen, specimens:"
	corpus4gramspecdict = corpus4gramspecdict.most_common()
	corpus4gramspecdict = OrderedDict(corpus4gramspecdict)
	for key in corpus4gramspecdict:
		corpusoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus4gramspecdict[key]), 'freq: ' + str(log10(float(corpus4gramspecdict[key])/float(fourgramcorpuscount))))

	corpusoutput += "\n\t\ttype, types, typical, typify, typifies, typifying:"
	corpus4gramtypdict = corpus4gramtypdict.most_common()
	corpus4gramtypdict = OrderedDict(corpus4gramtypdict)
	for key in corpus4gramtypdict:
		corpusoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus4gramtypdict[key]), 'freq: ' + str(log10(float(corpus4gramtypdict[key])/float(fourgramcorpuscount))))

	corpusoutput += "\n\t\tspecies:"
	corpus4gramspeciesdict = corpus4gramspeciesdict.most_common()
	corpus4gramspeciesdict = OrderedDict(corpus4gramspeciesdict)
	for key in corpus4gramspeciesdict:
		corpusoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus4gramspeciesdict[key]), 'freq: ' + str(log10(float(corpus4gramspeciesdict[key])/float(fourgramcorpuscount))))

	corpusoutput += "\n\t\tgenus, genera:"
	corpus4gramgendict = corpus4gramgendict.most_common()
	corpus4gramgendict = OrderedDict(corpus4gramgendict)
	for key in corpus4gramgendict:
		corpusoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus4gramgendict[key]), 'freq: ' + str(log10(float(corpus4gramgendict[key])/float(fourgramcorpuscount))))

	corpusoutput += "\n\t\tform:"
	corpus4gramformdict = corpus4gramformdict.most_common()
	corpus4gramformdict = OrderedDict(corpus4gramformdict)
	for key in corpus4gramformdict:
		corpusoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus4gramformdict[key]), 'freq: ' + str(log10(float(corpus4gramformdict[key])/float(fourgramcorpuscount))))

	corpusoutput += "\n\t\tsubspecies:"
	corpus4gramsubspeciesdict = corpus4gramsubspeciesdict.most_common()
	corpus4gramsubspeciesdict = OrderedDict(corpus4gramsubspeciesdict)
	for key in corpus4gramsubspeciesdict:
		corpusoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus4gramsubspeciesdict[key]), 'freq: ' + str(log10(float(corpus4gramsubspeciesdict[key])/float(fourgramcorpuscount))))

	corpusoutput += "\n\t\tecotype, ecotypes:"
	corpus4gramecodict = corpus4gramecodict.most_common()
	corpus4gramecodict = OrderedDict(corpus4gramecodict)
	for key in corpus4gramecodict:
		corpusoutput += "\n\t\t\t" + '{:45s} {:15s} {:25s}'.format(key, 'count: ' + str(corpus4gramecodict[key]), 'freq: ' + str(log10(float(corpus4gramecodict[key])/float(fourgramcorpuscount))))

	"""
	The following writes the corpus output string 
	to a file in the results directory.
	"""
	os.chdir('/Users/matthewnunez/Desktop/working/notebooks/results/')
	with open('corpus.txt', 'w') as f:
		f.write(corpusoutput)
	break
