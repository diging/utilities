
# coding: utf-8

# ## Requirements
# 
# This notebook was written for Python 2.7, and requires the following packages:
# - `lxml==4.0.0`
# - `elasticsearch==5.4.0`
# - `xmltodict==0.11.0h`

# ## Environment
# 
# Define environment variables:
# - `DATASET_DIR`:
# Path to the dataset directory.
# 
# - `ES_INDEX_NAME`:
# The elasticsearch index where you want the documents to be uploaded.
# 
# - `ES_DOCUMENT_TYPE`:
# The document type you want to use for each uploaded document.
# 
# - `ES_HOST`:
# The connection string for accessing Elasticsearch instance. The format is as follows:
# ```
# http://<username>:<password>@<host>:<port>
# ```
# Example: `http://user:pass@localhost:9200`. If the ES instance doesn't require authentication, you can specify `http://<host>:<port>` as the connection string. If `ES_HOST = ''`, `http://localhost:9200` will be used as the connection string.
# - `ES_CREATE_INDEX`:
# Create index if necessary.

# In[ ]:

import sys

if len(sys.argv) < 6:
    print 'Usage:\n\t JSTOR-Elasticsearch.py <dataset> <index-name> <es-host> <mappings-file> <log-prefix>\n'
    sys.exit(2)

DATASET_DIR      = sys.argv[1]
ES_INDEX_NAME    = sys.argv[2]
ES_HOST          = sys.argv[3]
MAPPINGS_JSON    = sys.argv[4]
LOG_PREFIX       = sys.argv[5]

ES_AUTH_USER = None
ES_AUTH_PASSWORD = None
if len(sys.argv) > 6:
    ES_AUTH_USER     = sys.argv[6]
    ES_AUTH_PASSWORD = sys.argv[7]

ES_DOCUMENT_TYPE = 'article'
ES_CREATE_INDEX  = True
ES_TIMEOUT = "60s"

DEBUG = ''

if DEBUG:
    ES_CREATE_INDEX = False

# ### Logging
# 
# To get realtime logs of processed directories, set ``'dataset'`` logger's level to `logging.INFO` or `logging.DEBUG`.  
#   
#   
# **Note**: `'elasticsearch'` logger generates high amounts of debug log statements.

# In[ ]:


import logging
import datetime
logger = logging.getLogger().setLevel(logging.CRITICAL)

logger = logging.getLogger('jstor')
DEBUG_LOG_FILENAME = '{}_debug.log'.format(LOG_PREFIX)
WARN_LOG_FILENAME = '{}_warn.log'.format(LOG_PREFIX)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
warning_handler = logging.FileHandler(WARN_LOG_FILENAME)
warning_handler.setLevel(level=logging.WARNING)
warning_handler.setFormatter(formatter)
debug_handler = logging.FileHandler(DEBUG_LOG_FILENAME)
debug_handler.setLevel(level=logging.DEBUG)
debug_handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(warning_handler)
logger.addHandler(debug_handler)

# ## Supporting Implementation
# 
# ### UTF8 encoding
# 
# *NOTE: This step is not needed for Python 3 and above.*  
# 
# Ensure all strings use `utf-8` encoding by default, else you may run into `ordinal not in range` errors.

# In[ ]:

import sys
reload(sys)
sys.setdefaultencoding('UTF8')


# ### Parsers

# In[ ]:


import re
import xml.etree.ElementTree as ET
import xmltodict

from lxml import etree

class LanguageError(Exception):
    pass

class XMLParser(object):
    def _process_if_avail(self, d, key, func, target=None):
        try:
            value = d.pop(key)
        except KeyError:
            return
        else:
            if value is not None:
                new_value = func(value)
                if new_value is not None:
                    d[target or key] = new_value

    def _process__article_meta__contrib_group(self, contrib_groups):
        if not isinstance(contrib_groups, list):
            contrib_groups = [contrib_groups]

        for contrib_group in contrib_groups:
            if not isinstance(contrib_group['contrib'], list):
                contrib_group['contrib'] = [contrib_group['contrib']]

            try:
                if isinstance(contrib_group['aff'], basestring):
                    contrib_group['aff'] = [contrib_group['aff']]
            except KeyError:
                pass

            for i, contrib in enumerate(contrib_group['contrib']):
                try:
                    name = contrib['string-name']
                except KeyError:
                    pass
                else:
                    if isinstance(name, basestring):
                        name = [name]
                    contrib_group['contrib'][i]['string-name'] = name
                try:
                    if isinstance(contrib['aff'], basestring):
                        contrib['aff'] = [contrib['aff']]
                except KeyError:
                    pass

        return contrib_groups

    def _process__article_meta__pub_date(self, pub_dates):
        years = None
        if isinstance(pub_dates, dict):
            if isinstance(pub_dates['year'], list):
                return pub_dates['year']
            else:
                return [pub_dates['year']]

        return [pub_date['year'] for pub_date in pub_dates]

    def _process__article_meta(self, article_meta):                                         
        _make_str = lambda d: d.get('#text', None) if isinstance(d, dict) else d

        # Remove duplicates
        for key in ('issue-id', 'issue', 'volume', 'pub-date'):
            if isinstance(article_meta.get(key, ''), list):
                if article_meta[key][0] == article_meta[key][1]:
                    article_meta[key] = article_meta[key][0]

        self._process_if_avail(article_meta, 'pub-date', self._process__article_meta__pub_date, 'year')
        # self._process_if_avail(article_meta, 'contrib-group', self._process__article_meta__contrib_group)
        # self._process_if_avail(article_meta, 'issue-id', _make_str)
        # self._process_if_avail(article_meta, 'issue', _make_str)
        # self._process_if_avail(article_meta, 'volume', _make_str)

        try:
            self._process_if_avail(article_meta['title-group'], 'article-title', _make_str)
        except KeyError:
            pass
        return article_meta

    def _process__journal_meta(self, journal_meta):
        journal_title_str = lambda journal_title: journal_title['#text'] if isinstance(journal_title, dict) else journal_title
        self._process_if_avail(journal_meta['journal-title-group'], 'journal-title', journal_title_str)
        try:
            journal_meta['journal-title'] = journal_meta.pop('journal-title-group')['journal-title']
        except KeyError:
            pass
        return journal_meta

    def _get_parse_postprocessor(self, article_et):
        etree_str = lambda e: etree.tostring(e, encoding='utf-8', method='text').strip()
        isenglish = lambda x: re.match(x, 'eng?', re.I)
        def postprocessor(path, key, value):
            xpath = '/'.join((path[i][0] for i in xrange(1, len(path))))

            if key == '@xml:lang' and not isenglish(value):
                raise LanguageError(value)

            if xpath == 'front/article-meta/custom-meta-group/custom-meta/meta-value' and not isenglish(value):
                raise LanguageError(value)

            if value is None:
                return None

            if key in set((
                '@xmlns:xsi',
                '@xml:lang',
                '@xlink:type',
                '@ext-link-type',
                '@content-type',
                '@dtd-version',
                '@xmlns:oasis',
                '@xmlns:xlink',
                '@xmlns:mml',
                '@xlink:role',
                '@xlink:title',
                '@article-type',
                'fig-count',
                'equation-count',
                'table-count',
                )):
                return None

            if re.search('|'.join((
                '^front/article-meta/kwd-group/x',
                '^front/article-meta/contrib-group/x',
                '^front/article-meta/contrib-group/xref',
                '^front/article-meta/contrib-group/contrib/x',
                '^front/article-meta/contrib-group/contrib/xref',
                '^front/article-meta/related-article',
                '^front/article-meta/product',
                '^front/article-meta/permissions',
                '^front/article-meta/custom-meta-group',
                '^front/article-meta/trans-abstract',
                '^front/article-meta/title-group/trans-title-group',
                '^front/article-meta/title-group/trans-title-group/trans-title',
                '^front/article-meta/article-categories/subj-group/subj-group',
                '^front/journal-meta/custom-meta-group',
                '^body',
                )), xpath):
                return None

            if key == 'email':
                if isinstance(value, dict):
                    value = value['#text']
                return key, value

            if key in set((
                'page-count',
                'ref-count',
                )):
                return key, int(value['@count'])

            if xpath == 'front/article-meta/self-uri' and not isinstance(value, basestring):
                return key, value['@xlink:href']

            if key == 'address':
                return key, value['addr-line']

            # Single occurence
            path_list = (
                'front/article-meta/abstract',
                'front/article-meta/author-notes',
                'front/article-meta/bio',
                )
            if xpath in set(path_list) and not key.startswith('@'):
                element = article_et.xpath(xpath + '[not(@processed="true")]')[0]
                value = etree_str(element).strip()
                element.set('processed', 'true')
                if not value:
                    return None
                return key, value
            if re.search('|'.join(map(lambda x: '^'+x, path_list)), xpath):
                return None

            # Multiple lines per occurrence
            path_list = (
                'back/app-group/app',
                'back/fn-group',
                'back/sec',
                'front/article-meta/contrib-group/fn',
                )
            if xpath in set(path_list) and not key.startswith('@'):
                element = article_et.xpath(xpath + '[not(@processed="true")]')[0]
                value = etree_str(element).strip()
                element.set('processed', 'true')
                if not value:
                    return None
                return key, value
            if re.search('|'.join(map(lambda x: '^'+x, path_list)), xpath):
                return None

            # Multiple lines per occurrence
            if key in set((
                'notes',
                'bio',
                'ack',
                'fn',
                'sec',
                'app',
                )):
                element = article_et.xpath(xpath + '[not(@processed="true")]')[0]
                value = etree_str(element).strip()
                element.set('processed', 'true')
                if not value:
                    return None
                return key, value

            # Single line per occurrence
            if key in set((
                'aff',
                'collab',
                'string-name',
                'title',
                'subtitle',
                'label',
                'mixed-citation',
                'subject',
                'kwd',
                'addr-line',
                'article-title',
                'issue-id',
                'issue',
                'volume',
                )):
                element = article_et.xpath(xpath + '[not(@processed="true")]')[0]
                value = etree_str(element).strip()
                element.set('processed', 'true')
                if not value:
                    return None
                return key, re.sub('\s+', ' ', value)

            return key, value

        return postprocessor

    def parse(self, xml_path):
        article_et = etree.parse(xml_path, parser=etree.XMLParser(recover=True)).getroot()
        front = article_et.xpath('front')[0]
        front_back = front.xpath('back')
        front_body = front.xpath('body')
        if front_back:
            back = front_back[0]
            front.remove(back)
            article_et.append(back)
        if front_body:
            body = front_body[0]
            front.remove(body)
            article_et.append(body)

        if not front_body and not front_back:
            with open(xml_path, 'r') as fh:
                article = xmltodict.parse(fh.read(),
                        postprocessor=self._get_parse_postprocessor(article_et),
                        force_list=('string-name', 'contrib-group', 'contrib', 'aff'),
                        )['article']
        else:
            article = xmltodict.parse(etree.tostring(article_et), postprocessor=self._get_parse_postprocessor(article_et))['article']

        article['front']['journal-meta'] = self._process__journal_meta(article['front']['journal-meta'])
        article['front']['article-meta'] = self._process__article_meta(article['front']['article-meta'])

        self._process_if_avail(article['front'], 'notes', lambda v: v if isinstance(v, list) else [v])
        self._process_if_avail(article.get('back', {}), 'sec', lambda v: v if isinstance(v, list) else [v])

        article.update(article.pop('front'))

        try:
            article.update(article.pop('back'))
        except KeyError:
            pass

        return article

class TXTParser(object):
    def parse(self, txt_path):
        txt_root = ET.parse(txt_path).getroot()
        if txt_root.tag == 'plain_text':
            page_seq = [(p.attrib['sequence'], p.text) for p in list(txt_root)]
            page_seq.sort(key=lambda x: x[0])
            plain_text_pages = [p for s, p in page_seq]
            return {'plain_text': plain_text_pages}
        elif txt_root.tag == 'body':
            return {'body': ET.tostring(txt_root, encoding='utf-8', method='text')}


# ### Dataset article actions generator

# In[ ]:


import os

def generate_actions(dataset_dir, index, document_type):
    abs_dataset_dir = os.path.abspath(os.path.expanduser(dataset_dir))
    xmlparser = XMLParser()
    txtparser = TXTParser()
    doc_id = es.count(index, document_type)['count']

    if DEBUG:
        abs_dataset_dir = DEBUG
        import pdb; pdb.set_trace()

    for (dpath, dnames, fnames) in os.walk(abs_dataset_dir,topdown = False):
    
        if dnames:
            dnames.sort()

        if not fnames:
            continue
        

        logger.debug('Processing %s' % dpath)
        document = {}

        xml_files = [p for p in fnames if p.lower().endswith('.xml')]
        txt_files = [p for p in fnames if p.lower().endswith('.txt')]
        
        
        if len(xml_files)>0:
            for xml_file in xml_files:
                xml_path = os.path.join(dpath, xml_file)
                
                try:
                    document['article'] = xmlparser.parse(os.path.join(dpath, xml_path))
                except LanguageError, e:
                    logger.warning('{}: language \'{}\' not en/eng'.format(xml_path, e))
                    continue
                except Exception, e:
                    logger.error('{}: {}'.format(xml_path, e))
                    continue
                action = {
                    '_index': index,
                    '_type': document_type,
                    '_id': doc_id,
                    '_source': document
                }
                doc_id += 1
                yield action
                
        if len(txt_files) > 0:
            for txt_file in txt_files:
                txt_path = os.path.join(dpath, txt_file)
                
                try:
                    document.update(txtparser.parse(txt_path))
                except LanguageError, e:
                    logger.error('{}: {}'.format(txt_path, e))
                    continue
                
                action = {
                    '_index': index,
                    '_type': document_type,
                    '_id': doc_id,
                    '_source': document
                }
                doc_id += 1
                yield action
            
                
        
# ## Upload to ES
# 
# #### Imports

# In[ ]:


import elasticsearch
import elasticsearch.helpers


# #### Get client

# In[ ]:

if ES_AUTH_USER:
    print "Using authentication for " + ES_AUTH_USER
    es = elasticsearch.Elasticsearch([ES_HOST], http_auth=ES_AUTH_USER+":"+ES_AUTH_PASSWORD, connection_class=elasticsearch.RequestsHttpConnection) if ES_HOST else elasticsearch.Elasticsearch()
else:
    es = elasticsearch.Elasticsearch([ES_HOST]) if ES_HOST else elasticsearch.Elasticsearch()


# #### Create Index
# 
# Create index if necessary.

# In[ ]:


# es.indices.delete(index=ES_INDEX_NAME)
import json
if ES_CREATE_INDEX:
    with open(MAPPINGS_JSON, 'r') as fh:
        mappings = json.load(fh).values()[0]
    es.indices.create(index=ES_INDEX_NAME, body=mappings)


# #### Start Upload
# 
# Start (bulk) uploading documents to Elasticsearch. Use `chunk_size` parameter to control how many documents are uploaded in one request. By default, at most `500` documents are uploaded per request.  
# 
# Depending on the log level, real- logs of processed directories may be displayed.

# In[ ]:


action_generator = generate_actions(DATASET_DIR, index=ES_INDEX_NAME, document_type=ES_DOCUMENT_TYPE)

# elasticsearch.helpers.bulk(es, action_generator, chunk_size=100)
elasticsearch.helpers.bulk(es, action_generator, timeout=ES_TIMEOUT)


# #### Test
# 
# The following command just gets the count of documents.

# In[ ]:


es.count(index=ES_INDEX_NAME, doc_type=ES_DOCUMENT_TYPE)['count']

