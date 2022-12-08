library(igraph)

g <- read.graph("edges.txt", format="edgelist")
length(E(g))
length(V(g))
diameter(g)
transitivity(g)
degree.distribution(g)
page_rank <- page_rank(g)$vector
node_size = page_rank*20
plot(g, vertex.label=NA, vertex.size=node_size)


wc <- walktrap.community(g)
modularity(wc)
membership(wc)
plot(g, vertex.color=membership(wc))

h <- hist(membership(wc), breaks=c(0,1,2,3,4,5,6,7,8))
text(h$mids,h$counts,labels=h$counts, adj=c(0.5, -0.5))

h
     