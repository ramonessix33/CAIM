"""
.. module:: CountWords
CountWords
*************
:Description: CountWords
    Generates a list with the counts and the words in the 'text' field of the documents in an index
:Authors: bejar

:Version:
:Created on: 04/07/2017 11:58
"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from elasticsearch.exceptions import NotFoundError, TransportError
import matplotlib.pyplot as plt
#import enchant


import argparse

__author__ = 'bejar'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, required=True, help='Index to search')
    parser.add_argument('--alpha', action='store_true', default=False, help='Sort words alphabetically')
    args = parser.parse_args()

    index = args.index

    d = enchant.Dict("en_US")

    cNum = 0
    cSpellCheck = 0
    cStopWords = 0
    stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now']

    try:
        client = Elasticsearch(timeout=1000)
        voc = {}
        sc = scan(client, index=index, query={"query" : {"match_all": {}}})
        for s in sc:
            try:
                tv = client.termvectors(index=index, id=s['_id'], fields=['text'])
                if 'text' in tv['term_vectors']:
                    for t in tv['term_vectors']['text']['terms']:
                        if (not t.isalpha()) :
                            cNum += 1
                            continue
                        #if t in stopwords:
                        #    cStopWords += 1
                        #    continue
                        #if not d.check(t):
                        #    cSpellCheck += 1
                        #    continue

                        if t in voc:
                            voc[t] += tv['term_vectors']['text']['terms'][t]['term_freq']
                        else:
                            voc[t] = tv['term_vectors']['text']['terms'][t]['term_freq']
            except TransportError:
                pass
        lpal = []
        freq = []

        for v in voc:
            lpal.append((v.encode("utf-8", "ignore"), voc[v]))

        for pal, cnt in sorted(lpal, key=lambda x: x[0 if args.alpha else 1]):
            print(f'{cnt}, {pal.decode("utf-8")}')
            freq.append(cnt)
        print('--------------------')
        print(f'{len(lpal)} Words')
        print('############################################')
        print("Paraules mal escrites " + str(cSpellCheck))
        print('Stopwords llevades ' + str(cStopWords))
        print('Num llevatss ' + str(cNum))
        plt.plot(freq)
        plt.show()
    except NotFoundError:
        print(f'Index {index} does not exists')
