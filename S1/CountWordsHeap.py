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
from scipy.optimize import curve_fit


import argparse

__author__ = 'bejar'
maxNum = 500


def f (x, k, b):
    return k*(x**b)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--alpha', action='store_true', default=False, help='Sort words alphabetically')
    args = parser.parse_args()

    x = []
    y = []
    for i in [1, 5, 10, 15, 20, 25, 30]:
        index = "novels"+str(i)
        try:
            diffWords = 0
            paraulesTotals = 0
            b = False
            client = Elasticsearch(timeout=1000)
            voc = {}
            sc = scan(client, index=index, query={"query" : {"match_all": {}}})
            for s in sc:
                try:
                    tv = client.termvectors(index=index, id=s['_id'], fields=['text'])
                    if 'text' in tv['term_vectors']:
                        for t in tv['term_vectors']['text']['terms']:
                            if (not t.isalpha()) :
                                continue
                            paraulesTotals += 1
                            if t in voc:
                                voc[t] += tv['term_vectors']['text']['terms'][t]['term_freq']
                            else:
                                diffWords += 1
                                voc[t] = tv['term_vectors']['text']['terms'][t]['term_freq']
                except TransportError:
                    pass
                if b:
                    break
            x.append(paraulesTotals)
            y.append(diffWords)
            print("Paraules Totals :" + str(paraulesTotals) + " Paraules Diferentes: " + str(diffWords))
        except NotFoundError:
            print(f'Index {index} does not exists')


    params, covs = curve_fit(f, x, y)
    print("params: ", params)
    k, b = params[0], params[1]
    yfit = k*(x**b)

    #plt.xscale("log")
    #plt.yscale("log")
    plt.plot(x, y, 'bo', label="y-original")
    plt.plot(x, yfit, label="yfit")
    plt.xlabel('Paraules Totals')
    plt.ylabel('Paraules Diferentes')
    plt.legend(loc='best', fancybox=True, shadow=True)
    plt.grid(True)
    plt.show()
