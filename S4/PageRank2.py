#!/usr/bin/python

from collections import namedtuple
import time
import sys
import matplotlib.pyplot as plt

class Edge:
    def __init__ (self, origin=None):
        self.origin = origin # write appropriate value
        self.weight = 1 # write appropriate value

    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)

    ## write rest of code that you need for this class

class Airport:
    def __init__ (self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = []
        self.routeHash = dict()
        self.outweight =  0  # write appropriate value
        self.pageIndex = 0

    def __repr__(self):
        return f"{self.code}\t{self.pageIndex}\t{self.name}"

edgeList = [] # list of Edge
edgeHash = dict() # hash of edge to ease the match
airportList = [] # list of Airport
airportHash = dict() # hash key IATA code -> Airport
p = []

def readAirports(fd):
    print("Reading Airport file from {0}".format(fd))
    airportsTxt = open(fd, "r");
    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp[4]) != 5 :
                raise Exception('not an IATA code')
            a.name=temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code=temp[4][1:-1]
        except Exception as inst:
            pass
        else:
            a.pageIndex = cont
            cont += 1
            airportList.append(a)
            airportHash[a.code] = a
    airportsTxt.close()
    print(f"There were {cont} Airports with IATA code")

def readRoutes(fd):
    print("Reading Routes file from {fd}")
    routesTxt = open(fd, "r");
    for line in routesTxt.readlines():
        temp = line.split(',')
        locations =[]
        for i in temp:
            if (i.isalpha() and i in airportHash):
                locations.append(i)
        if (len(locations) != 2):
            continue
        airportHash[locations[0]].outweight += 1
        if not locations[1] in edgeHash.keys():
            edgeHash[locations[1]] = {}
        if locations[0] in edgeHash[locations[1]].keys():
            edgeHash[locations[1]][locations[0]].weight += 1
            airportHash[locations[0]].routeHash[locations[1]] +=1
        else:
            edgeHash[locations[1]][locations[0]] = Edge(locations[0])
            airportHash[locations[0]].routeHash[locations[1]] = 1
            airportHash[locations[0]].routes.append(locations[1])

    routesTxt.close()

def computePageRanks(L):
    num_air = len(airportList)
    global p
    p = [1/num_air]*num_air
    epsilon = ((1 - L) / num_air) / 100
    n = 0
    while n < 1000:
        Q = [0]*num_air
        dif = 0
        for i in range(num_air):
            x = airportList[i].code
            Q[i] = 0
            if x in edgeHash.keys():
                suma = 0
                for j in edgeHash[x].values():
                    y = airportHash[j.origin]
                    s = p[y.pageIndex]
                    s *= edgeHash[x][j.origin].weight
                    s /= y.outweight
                    suma += s
                Q[i] = L * suma
            Q[i] += (1-L)/num_air
        total = sum(Q)
        Q = list(map((lambda x: x / total), Q))
        dif = max(map(lambda x,y: abs(x-y),p,Q))
        p = Q
        n += 1
        if dif < epsilon:
            break
    return n


def outputPageRanks():
    print("Output Ranks")
    # write your code
    out = map((lambda x,y: (x,y.code)), p, airportList)
    outSorted = sorted(out, reverse=True)
    for i in range(len(outSorted)):
        print(i, outSorted[i], airportHash[outSorted[i][1]].name)
    print("Suma de la llista: " + str(sum(p)))

def main(argv=None):
    readAirports("airports1.txt")
    readRoutes("routes1.txt")
    Lambdas = [0.3,0.5,0.8,0.81,0.83,0.85,0.87,0.9]
    l = 0.1
    Ls = []
    Its = []
    while l < 1:
        time1 = time.time()
        iterations = computePageRanks(l)
        time2 = time.time()
        print("L: ", l)
        print("#Iterations:", iterations)
        print("Time of computePageRanks():", time2-time1)
        Ls.append(l)
        Its.append(iterations)
        l+=0.05
    plt.plot(Ls, Its)
    plt.title("Iteracions per Valor d'L")
    plt.xlabel('L')
    plt.ylabel('Iteracions')
    plt.show()

if __name__ == "__main__":
    sys.exit(main())






