from re import L
from numpy import array, exp
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt 
import csv
import math

def f (rank, c, b, a):
    return c / ((rank+b)**a)

line_count = 0
x = []
y = []

with open('news.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    b = True
    for row in csv_reader:
        if b:
            if row[0] == "--------------------":
                b = False
            else:
                line_count += 1
                x.append(line_count)
                y.append(int(row[0]))

y.reverse()

params, covs = curve_fit(f, x, y) 
print("params: ", params) 
c, b, a = params[0], params[1], params[2]
yfit = c / ((x+b)**a)

#plt.xscale("log")
#plt.yscale("log")
plt.plot(x, y, 'bo', label="y-original")
plt.plot(x, yfit, label="yfit")
plt.xlabel('x')
plt.ylabel('y')
plt.legend(loc='best', fancybox=True, shadow=True)
plt.grid(True)
plt.show() 