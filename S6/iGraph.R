library(igraph)

i <- 0
trans <- c()
avgShPth <- c()
p <- 10^(seq(-4,0,0.25))
for (i in p) {
  ws <- watts.strogatz.game(1, 1000, 4, i)
  trans <- append(trans, transitivity(ws))
  avgShPth <- append(avgShPth, average.path.length(ws))
}
trans <- trans / trans[1]
avgShPth <- avgShPth / avgShPth[1]

plot(p,trans, ylim = c(0,1), ylab='coeff', log='x')
points(p,avgShPth, ylim = c(0,1), ylab='coeff',pch=15)



