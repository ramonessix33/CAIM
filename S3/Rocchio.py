from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch.client import CatClient
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q
import heapq

import argparse

import numpy as np

__author__ = 'bejar'

def search_file_by_path(client, index, path):
    """
    Search for a file using its path
    :param path:
    :return:
    """
    s = Search(using=client, index=index)
    q = Q('match', path=path)  # exact search in the path field
    s = s.query(q)
    result = s.execute()

    lfiles = [r for r in result]
    if len(lfiles) == 0:
        raise NameError(f'File [{path}] not found')
    else:
        return lfiles[0].meta.id


def document_term_vector(client, index, id):
    """
    Returns the term vector of a document and its statistics a two sorted list of pairs (word, count)
    The first one is the frequency of the term in the document, the second one is the number of documents
    that contain the term
    :param client:
    :param index:
    :param id:
    :return:
    """
    termvector = client.termvectors(index=index, id=id, fields=['text'],
                                    positions=False, term_statistics=True)

    file_td = {}
    file_df = {}

    if 'text' in termvector['term_vectors']:
        for t in termvector['term_vectors']['text']['terms']:
            file_td[t] = termvector['term_vectors']['text']['terms'][t]['term_freq']
            file_df[t] = termvector['term_vectors']['text']['terms'][t]['doc_freq']
    return sorted(file_td.items()), sorted(file_df.items())

def toTFIDF(client, index, file_id):
    """
    Returns the term weights of a document
    :param file:
    :return:
    """

    # Get the frequency of the term in the document, and the number of documents
    # that contain the term
    file_tv, file_df = document_term_vector(client, index, file_id)

    max_freq = max([f for _, f in file_tv])

    dcount = doc_count(client, index)

    tfidfw = []
    tokens = []
    for (t, w),(_, df) in zip(file_tv, file_df):
        tf = w/max_freq
        idf = np.log2(dcount / df)
        tfidfw.append((tf*idf))
        tokens.append(t)
        pass

    return list(zip(tokens, normalize(tfidfw)))

def print_term_weigth_vector(twv):
    """
    Prints the term vector and the correspondig weights
    :param twv:
    :return:
    """
    #
    for t in twv:
        print(str(t))
    #
    pass


def normalize(tw):
    """
    Normalizes the weights in t so that they form a unit-length vector
    It is assumed that not all weights are 0
    :param tw:
    :return:
    """
    #
    s = 0
    for t in tw:
        s+= t*t
    #
    s = np.sqrt(s)
    tw2 = tw/s
    return tw2


def cosine_similarity(tw1, tw2):
    """
    Computes the cosine similarity between two weight vectors, terms are alphabetically ordered
    :param tw1:
    :param tw2:
    :return:
    """
    #
    s = 0
    sizetw1, sizetw2 = (len(list(tw1)), len(list(tw2)))
    indextw1, indextw2 = (0, 0)
    while indextw1 < sizetw1 and indextw2 < sizetw2:
        if tw1[indextw1][0] == tw2[indextw2][0]:
            s += tw1[indextw1][1] * tw2[indextw2][1]
            indextw1 += 1
            indextw2 += 1
        elif tw1[indextw1][0] > tw2[indextw2][0]:
            indextw2 += 1
        else:
            indextw1 += 1
    return s

def doc_count(client, index):
    """
    Returns the number of documents in an index
    :param client:
    :param index:
    :return:
    """
    return int(CatClient(client).count(index=[index], format='json')[0]['count'])

def convertir_dic(weights):
    dic = {}
    for (word, weight) in weights:
        dic[word]=weight
    return dic

def query_a_diccionari(query):
    dic = {}
    for i in query:
        if '^' in i:
            word, value = i.split('^')
            dict[word] = int(value)
        else:
            dic[i] = 1
    return dic

def diccionari_a_query(dic):
    query = []
    for i in set(dic):
        query.append(i + "^" + str(dic[i]))
    return query

def rocchio(query, docs, index, alpha, beta, R):
    d = []
    for f in docs:
        d.append(convertir_dic(toTFIDF(client, index, f.meta.id)))
    sumd = d[0]
    for dic in d[1:]:
        sumd = {x: sumd.get(x, 0) + dic.get(x, 0) for x in set(sumd).union(dic)}
    sumd = heapq.nlargest(R, sumd.items(), key=lambda i: i[1])
    k = len(docs)
    sumd = {x: beta*y/k for (x,y) in sumd}
    newQuery = {x: alpha*query.get(x, 0) for x in set(query)}
    return diccionari_a_query({x: sumd.get(x, 0) + newQuery.get(x, 0) for x in set(sumd).union(newQuery)})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, help='Index to search')
    parser.add_argument('--query', default=None, nargs=argparse.REMAINDER, help='List of words to search')

    args = parser.parse_args()

    index = args.index
    query = args.query
    print(query)
    nhits = 5
    nrounds = 5
    alpha = 1
    beta = 1
    R = 10
    #if query is None:
    #    raise Exception("Insereix Query")
    try:
        client = Elasticsearch()
        s = Search(using=client, index=index)

        for i in range(1,nrounds):
            print(i)
            print(query)
            q = Q('query_string',query=query[0])
            for i in range(1, len(query)):
                q &= Q('query_string',query=query[i])

            s = s.query(q)
            response = s[0:nhits].execute()
            query = rocchio(query_a_diccionari(query),response, index, alpha, beta, R)

        # Last Query
        q = Q('query_string',query=query[0])
        for i in range(1, len(query)):
            q &= Q('query_string',query=query[i])

        s = s.query(q)
        response = s[0:nhits].execute()
        for r in response:  # only returns a specific number of results
            print(f'ID= {r.meta.id} SCORE={r.meta.score}')
            print(f'PATH= {r.path}')
            print(f'TEXT: {r.text[:50]}')
            print('-----------------------------------------------------------------')

        else:
            print('No query parameters passed')

        print (f"{response.hits.total['value']} Documents")

    except NotFoundError:
        print(f'Index {index} does not exists')
