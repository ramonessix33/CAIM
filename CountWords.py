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
import enchant


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
                        if not d.check(t):
                            cSpellCheck += 1
                            continue
                        
                        if t in voc:
                            voc[t] += tv['term_vectors']['text']['terms'][t]['term_freq']
                        else:
                            voc[t] = tv['term_vectors']['text']['terms'][t]['term_freq']
            except TransportError:
                pass
        lpal = []
        

        for v in voc:
            lpal.append((v.encode("utf-8", "ignore"), voc[v]))


        for pal, cnt in sorted(lpal, key=lambda x: x[0 if args.alpha else 1]):
            print(f'{cnt}, {pal.decode("utf-8")}')
        print('--------------------')
        print(f'{len(lpal)} Words')
        print("Paraules mal escrites " + str(cSpellCheck))
    except NotFoundError:
        print(f'Index {index} does not exists')
