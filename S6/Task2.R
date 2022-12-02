library(igraph)

g <- read.graph("edges.txt", format="edgelist")
length(E(g))
length(V(g))
diameter(g)
transitivity(g)
degree.distribution(g)

1. Describe the network a little. How many edges and nodes does it have? What is its diameter? And transitivity?
  And degree distribution? Does it look like a random network? Visualize the network with node sizes proportional
to their pagerank.
2. Now, use a community detection algorithm of your choice from the list provided. How many nodes does the
largest community found contain? Plot the histogram of community sizes. Plot the graph with its communities.
