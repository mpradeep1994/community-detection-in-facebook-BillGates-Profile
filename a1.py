from collections import Counter, defaultdict, deque
import copy
import math
import networkx as nx
import urllib.request



def example_graph():
    """
    Create the example graph from class. Used for testing.
    Do not modify.
    """
    g = nx.Graph()
    g.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'C'), ('B', 'D'), ('D', 'E'), ('D', 'F'), ('D', 'G'), ('E', 'F'), ('G', 'F')])
    return g




def bfs(graph, root, max_depth):
    """
    Perform breadth-first search to compute the shortest paths from a root node to all
    other nodes in the graph. To reduce running time, the max_depth parameter ends
    the search after the specified depth.
    E.g., if max_depth=2, only paths of length 2 or less will be considered.
    This means that nodes greather than max_depth distance from the root will not
    appear in the result.
    You may use these two classes to help with this implementation:
      https://docs.python.org/3.5/library/collections.html#collections.defaultdict
      https://docs.python.org/3.5/library/collections.html#collections.deque
    Params:
      graph.......A networkx Graph
      root........The root node in the search graph (a string). We are computing
                  shortest paths from this node to all others.
      max_depth...An integer representing the maximum depth to search.
    Returns:
      node2distances...dict from each node to the length of the shortest path from
                       the root node
      node2num_paths...dict from each node to the number of shortest paths from the
                       root node that pass through this node.
      node2parents.....dict from each node to the list of its parents in the search
                       tree
    In the doctests below, we first try with max_depth=5, then max_depth=2.
    >>> node2distances, node2num_paths, node2parents = bfs(example_graph(), 'E', 5)
    >>> sorted(node2distances.items())
    [('A', 3), ('B', 2), ('C', 3), ('D', 1), ('E', 0), ('F', 1), ('G', 2)]
    >>> sorted(node2num_paths.items())
    [('A', 1), ('B', 1), ('C', 1), ('D', 1), ('E', 1), ('F', 1), ('G', 2)]
    >>> sorted((node, sorted(parents)) for node, parents in node2parents.items())
    [('A', ['B']), ('B', ['D']), ('C', ['B']), ('D', ['E']), ('F', ['E']), ('G', ['D', 'F'])]
    >>> node2distances, node2num_paths, node2parents = bfs(example_graph(), 'E', 2)
    >>> sorted(node2distances.items())
    [('B', 2), ('D', 1), ('E', 0), ('F', 1), ('G', 2)]
    >>> sorted(node2num_paths.items())
    [('B', 1), ('D', 1), ('E', 1), ('F', 1), ('G', 2)]
    >>> sorted((node, sorted(parents)) for node, parents in node2parents.items())
    [('B', ['D']), ('D', ['E']), ('F', ['E']), ('G', ['D', 'F'])]
    """
    distance = {}
    distance[root] = 0
    path = {}
    path[root] = 1
    parent_dict ={}
    
    depth = 1
    
    to_process_node = deque()
    process_node = deque()
    process_node.append(root)
    
    n  =defaultdict()
    for i in graph:
        n[i]= graph.neighbors(i)

  
    while depth <= max_depth:
        while len(process_node)>0:
            parent = process_node.popleft()
            for neighbor in n[parent]:
                to_process_node.append(neighbor)
                if neighbor not in distance.keys():
                    distance[neighbor] = depth
                    parent_dict[neighbor]=[parent]
                elif neighbor in distance.keys() and distance[neighbor] == depth:
                    parent_dict[neighbor].append(parent) 
                    
        depth = depth +1
        for m in to_process_node:
            process_node.append(m)
        to_process_node.clear()
    
    for i in parent_dict:
        path[i] = len(parent_dict[i])
    
    return distance,path,parent_dict




def complexity_of_bfs(V, E, K):
    """
    If V is the number of vertices in a graph, E is the number of
    edges, and K is the max_depth of our approximate breadth-first
    search algorithm, then what is the *worst-case* run-time of
    this algorithm? As usual in complexity analysis, you can ignore
    any constant factors. E.g., if you think the answer is 2V * E + 3log(K),
    you would return V * E + math.log(K)
    >>> v = complexity_of_bfs(13, 23, 7)
    >>> type(v) == int or type(v) == float
    True
    """
    ###TODO
    return (V+E)*math.log(K)
    pass



def bottom_up(root, node2distances, node2num_paths, node2parents):
    """
    Compute the final step of the Girvan-Newman algorithm.
    See p 352 From your text:
    https://github.com/iit-cs579/main/blob/master/read/lru-10.pdf
        The third and final step is to calculate for each edge e the sum
        over all nodes Y of the fraction of shortest paths from the root
        X to Y that go through e. This calculation involves computing this
        sum for both nodes and edges, from the bottom. Each node other
        than the root is given a credit of 1, representing the shortest
        path to that node. This credit may be divided among nodes and
        edges above, since there could be several different shortest paths
        to the node. The rules for the calculation are as follows: ...
    Params:
      root.............The root node in the search graph (a string). We are computing
                       shortest paths from this node to all others.
      node2distances...dict from each node to the length of the shortest path from
                       the root node
      node2num_paths...dict from each node to the number of shortest paths from the
                       root node that pass through this node.
      node2parents.....dict from each node to the list of its parents in the search
                       tree
    Returns:
      A dict mapping edges to credit value. Each key is a tuple of two strings
      representing an edge (e.g., ('A', 'B')). Make sure each of these tuples
      are sorted alphabetically (so, it's ('A', 'B'), not ('B', 'A')).
      Any edges excluded from the results in bfs should also be exluded here.
    >>> node2distances, node2num_paths, node2parents = bfs(example_graph(), 'E', 5)
    >>> result = bottom_up('E', node2distances, node2num_paths, node2parents)
    >>> sorted(result.items())
    [(('A', 'B'), 1.0), (('B', 'C'), 1.0), (('B', 'D'), 3.0), (('D', 'E'), 4.5), (('D', 'G'), 0.5), (('E', 'F'), 1.5), (('F', 'G'), 0.5)]
    """
    sortdis = sorted(node2distances.items(), key = lambda x: x[1], reverse = True)
    nodes_credits = {}
    edges_credits = {}
    
    
    for i in sortdis:
        if i[0] != root:
            nodes_credits[i[0]] = 1
        else:
            nodes_credits[i[0]] = 0
    
    for i in sortdis:
        if i[0] != root:
            
            credit = nodes_credits[i[0]]/node2num_paths[i[0]]
            parent = node2parents[i[0]]

            for j in parent:
                nodes_credits[j] =nodes_credits[j] + credit
    
                edge = sorted((i[0],j))
                edges_credits[tuple(edge)] = credit
  
    return edges_credits






def approximate_betweenness(graph, max_depth):
    
    """
    Compute the approximate betweenness of each edge, using max_depth to reduce
    computation time in breadth-first search.
    You should call the bfs and bottom_up functions defined above for each node
    in the graph, and sum together the results. Be sure to divide by 2 at the
    end to get the final betweenness.

    Params:
      graph.......A networkx Graph
      max_depth...An integer representing the maximum depth to search.

    Returns:
      A dict mapping edges to betweenness. Each key is a tuple of two strings
      representing an edge (e.g., ('A', 'B')). Make sure each of these tuples
      are sorted alphabetically (so, it's ('A', 'B'), not ('B', 'A')).

    >>> sorted(approximate_betweenness(example_graph(), 2).items())
    [(('A', 'B'), 2.0), (('A', 'C'), 1.0), (('B', 'C'), 2.0), (('B', 'D'), 6.0), (('D', 'E'), 2.5), (('D', 'F'), 2.0), (('D', 'G'), 2.5), (('E', 'F'), 1.5), (('F', 'G'), 1.5)]
    
    """
    
    bet = {}
    for i in graph:
        node2distances, node2num_paths, node2parents = bfs(graph, i,max_depth )
        result = bottom_up(i, node2distances, node2num_paths, node2parents)
        for j in result:
            if j not in bet.keys():
                bet[j] = result[j]/2
            else:
                bet[j] = bet[j] + (result[j]/2)
    return bet



def multi_sort(xx):
    return sorted(sorted(xx, key=lambda x:(x[0],x[1])), key=lambda x:x[1],reverse = True)



def is_approximation_always_right():
    """
    Look at the doctests for approximate betweenness. In this example, the
    edge with the highest betweenness was ('B', 'D') for both cases (when
    max_depth=5 and max_depth=2).

    Consider an arbitrary graph G. For all max_depth > 1, will it always be
    the case that the edge with the highest betweenness will be the same
    using either approximate_betweenness verses the exact computation?
    Answer this question below.

    In this function, you just need to return either the string 'yes' or 'no'
    (no need to do any actual computations here).
    >>> s = is_approximation_always_right()
    >>> type(s)
    <class 'str'>
    """
    ###TODO
    g = example_graph()
    result =  multi_sort(approximate_betweenness(g, 2).items())[0][0]
    value = "yes"
    for i in range(3,6):
        temp = multi_sort(approximate_betweenness(g, i).items())[0][0]
        if temp != result:
            value = "no"
    return value
    pass




def partition_girvan_newman(graph, max_depth):
    """
    Use your approximate_betweenness implementation to partition a graph.
    Unlike in class, here you will not implement this recursively. Instead,
    just remove edges until more than one component is created, then return
    those components.
    That is, compute the approximate betweenness of all edges, and remove
    them until multiple comonents are created.

    You only need to compute the betweenness once.
    If there are ties in edge betweenness, break by edge name (e.g.,
    (('A', 'B'), 1.0) comes before (('B', 'C'), 1.0)).

    Note: the original graph variable should not be modified. Instead,
    make a copy of the original graph prior to removing edges.
    See the Graph.copy method https://networkx.github.io/documentation/development/reference/generated/networkx.Graph.copy.html
    Params:
      graph.......A networkx Graph
      max_depth...An integer representing the maximum depth to search.
    
    Returns:
      A list of networkx Graph objects, one per partition.
    
    >>> components = partition_girvan_newman(example_graph(), 5)
    >>> components = sorted(components, key=lambda x: sorted(x.nodes())[0])
    >>> sorted(components[0].nodes())
    ['A', 'B', 'C']
    >>> sorted(components[1].nodes())
    ['D', 'E', 'F', 'G']
    """
    ###TODO
    cg = graph.copy();

    bet = multi_sort(approximate_betweenness(cg,max_depth).items())
    i = 0
    while nx.number_connected_components(cg) <= 1:
        cg.remove_edge(*bet[i][0])
        i = i + 1

    comp = [c for c in nx.connected_component_subgraphs(cg)]
    return comp
    pass 


def get_subgraph(graph, min_degree):
    """Return a subgraph containing nodes whose degree is
    greater than or equal to min_degree.
    We'll use this in the main method to prune the original graph.

    Params:
      graph........a networkx graph
      min_degree...degree threshold
    Returns:
      a networkx graph, filtered as defined above.

    >>> subgraph = get_subgraph(example_graph(), 3)
    >>> sorted(subgraph.nodes())
    ['B', 'D', 'F']
    >>> len(subgraph.edges())
    2
    """
    to_delete_nodes = []
    for n in graph:
        if graph.degree(n) < min_degree:
            to_delete_nodes.append(n)
    
    graph.remove_nodes_from(to_delete_nodes)
    return graph


# In[72]:

def volume(nodes, graph):
    """
    Compute the volume for a list of nodes, which
    is the number of edges in `graph` with at least one end in
    nodes.
    Params:
      nodes...a list of strings for the nodes to compute the volume of.
      graph...a networkx graph

    >>> volume(['A', 'B', 'C'], example_graph())
    4
    """
    ###TODO
    return len(graph.edges(nodes))


def cut(S, T, graph):
    """
    Compute the cut-set of the cut (S,T), which is
    the set of edges that have one endpoint in S and
    the other in T.
    Params:
      S.......set of nodes in first subset
      T.......set of nodes in second subset
      graph...networkx graph
    Returns:
      An int representing the cut-set.

    >>> cut(['A', 'B', 'C'], ['D', 'E', 'F', 'G'], example_graph())
    1
    """
    ###TODO
    count = 0
    for n in S:
        for m in T:
            if graph.has_edge(n,m):
                count = count+1
    return count


def norm_cut(S, T, graph):
    """
    The normalized cut value for the cut S/T. (See lec06.)
    Params:
      S.......set of nodes in first subset
      T.......set of nodes in second subset
      graph...networkx graph
    Returns:
      An float representing the normalized cut value

    """
    ###TODO
    ST_cut = cut(S,T,graph)
    S_volume = volume(S,graph)
    T_volume = volume(T,graph)
    norm = (ST_cut*1.0/S_volume)+(ST_cut*1.0/T_volume)
    return norm


# In[73]:

def score_max_depths(graph, max_depths):
    """
    In order to assess the quality of the approximate partitioning method
    we've developed, we will run it with different values for max_depth
    and see how it affects the norm_cut score of the resulting partitions.
    Recall that smaller norm_cut scores correspond to better partitions.

    Params:
      graph........a networkx Graph
      max_depths...a list of ints for the max_depth values to be passed
                   to calls to partition_girvan_newman

    Returns:
      A list of (int, float) tuples representing the max_depth and the
      norm_cut value obtained by the partitions returned by
      partition_girvan_newman. See Log.txt for an example.
    """
    ###TODO
    norm_list =[]
    node_set = set(graph.nodes()) 
    for depth in max_depths:
        components = partition_girvan_newman(graph, depth)
        norm_list.append((depth,norm_cut(components[0], components[1], graph)))
    return norm_list
            


# In[74]:

def make_training_graph(graph, test_node, n):
    """
    To make a training graph, we need to remove n edges from the graph.
    As in lecture, we'll assume there is a test_node for which we will
    remove some edges. Remove the edges to the first n neighbors of
    test_node, where the neighbors are sorted alphabetically.
    E.g., if 'A' has neighbors 'B' and 'C', and n=1, then the edge
    ('A', 'B') will be removed.

    Be sure to *copy* the input graph prior to removing edges.

    Params:
      graph.......a networkx Graph
      test_node...a string representing one node in the graph whose
                  edges will be removed.
      n...........the number of edges to remove.

    Returns:
      A *new* networkx Graph with n edges removed.

    In this doctest, we remove edges for two friends of D:
    >>> g = example_graph()
    >>> sorted(g.neighbors('D'))
    ['B', 'E', 'F', 'G']
    >>> train_graph = make_training_graph(g, 'D', 2)
    >>> sorted(train_graph.neighbors('D'))
    ['F', 'G']
    """
    
    cg = graph.copy()
    
    neighouring_nodes = sorted(cg.neighbors(test_node))
    for i in range(n):
        cg.remove_edge(test_node,neighouring_nodes[i])
        
    return cg


# In[75]:

def jaccard(graph, node, k):
    """
    Compute the k highest scoring edges to add to this node based on
    the Jaccard similarity measure.
    Note that we don't return scores for edges that already appear in the graph.

    Params:
      graph....a networkx graph
      node.....a node in the graph (a string) to recommend links for.
      k........the number of links to recommend.

    Returns:
      A list of tuples in descending order of score representing the
      recommended new edges. Ties are broken by
      alphabetical order of the terminal node in the edge.

    In this example below, we remove edges (D, B) and (D, E) from the
    example graph. The top two edges to add according to Jaccard are
    (D, E), with score 0.5, and (D, A), with score 0. (Note that all the
    other remaining edges have score 0, but 'A' is first alphabetically.)

    >>> g = example_graph()
    >>> train_graph = make_training_graph(g, 'D', 2)
    >>> jaccard(train_graph, 'D', 2)
    [(('D', 'E'), 0.5), (('D', 'A'), 0.0)]
    """
    jac_scores = []
    neighboring_node = set(graph.neighbors(node))
    for n in graph.nodes():
        if n != node and not graph.has_edge(node, n):
            new_neighbours = set(graph.neighbors(n))
            score = 1. * (len(neighboring_node & new_neighbours)) / (len(neighboring_node | new_neighbours))
            jac_scores.append(((node, n), score))
    jac_scores = multi_sort(jac_scores)
    
    return jac_scores[:k]


# In[76]:

def path_score(graph, root, k, beta):
    """
    Compute a new link prediction scoring function based on the shortest
    paths between two nodes, as defined above.

    Note that we don't return scores for edges that already appear in the graph.

    This algorithm should have the same time complexity as bfs above.

    Params:
      graph....a networkx graph
      root.....a node in the graph (a string) to recommend links for.
      k........the number of links to recommend.
      beta.....the beta parameter in the equation above.
    

    Returns:
      A list of tuples in descending order of score. Ties are broken by
      alphabetical order of the terminal node in the edge.

    In this example below, we remove edge (D, F) from the
    example graph. The top two edges to add according to path_score are
    (D, F), with score 0.5, and (D, A), with score .25. (Note that (D, C)
    is tied with a score of .25, but (D, A) is first alphabetically.)

    >>> g = example_graph()
    >>> train_graph = g.copy()
    >>> train_graph.remove_edge(*('D', 'F'))
    >>> path_score(train_graph, 'D', k=4, beta=.5)
    [(('D', 'F'), 0.5), (('D', 'A'), 0.25), (('D', 'C'), 0.25)]
    """
    ###TODO
    node2distances, node2numpaths, node2parents = bfs(graph,root,5)
    path_score_cal =[]
    
    for node in set(graph.nodes()) - set(graph.neighbors(root)):
        if node!=root:
            path_score_cal.append(((root,node),(beta **node2distances[node])*node2numpaths[node]))
        
    return multi_sort(path_score_cal)[:k]
    pass


# In[78]:

def evaluate(predicted_edges, graph):
    """
    Return the fraction of the predicted edges that exist in the graph.

    Args:
      predicted_edges...a list of edges (tuples) that are predicted to
                        exist in this graph
      graph.............a networkx Graph

    Returns:
      The fraction of edges in predicted_edges that exist in the graph.

    In this doctest, the edge ('D', 'E') appears in the example_graph,
    but ('D', 'A') does not, so 1/2 = 0.5

    >>> evaluate([('D', 'E'), ('D', 'A')], example_graph())
    0.5
    """
    ###TODO
    gp=[]
    edges=graph.edges()
    counter  = 0
    for i in predicted_edges:
        if i in edges or i[::-1] in edges:
            counter = counter +1
        
    return counter*1./len(predicted_edges)


# In[114]:

def download_data():
    """
    Download the data. Done for you.
    """
    urllib.request.urlretrieve('http://cs.iit.edu/~culotta/cs579/a1/edges.txt.gz', 'edges.txt.gz')


# In[80]:

def read_graph():
    """ Read 'edges.txt.gz' into a networkx **undirected** graph.
    Done for you.
    Returns:
      A networkx undirected graph.
    """
    return nx.read_edgelist('edges.txt.gz', delimiter='\t')


# In[115]:

def main():
    """
    FYI: This takes ~10-15 seconds to run on my laptop.
    """
    download_data()
    graph = read_graph()
    print('graph has %d nodes and %d edges' %
          (graph.order(), graph.number_of_edges()))
    subgraph = get_subgraph(graph, 2)
    print('subgraph has %d nodes and %d edges' %
          (subgraph.order(), subgraph.number_of_edges()))
    print('norm_cut scores by max_depth:')
    print(score_max_depths(subgraph, range(1,5)))
    clusters = partition_girvan_newman(subgraph, 3)
    print('first partition: cluster 1 has %d nodes and cluster 2 has %d nodes' %
          (clusters[0].order(), clusters[1].order()))
    print('cluster 2 nodes:')
    print(clusters[1].nodes())
    
    test_node = 'Bill Gates'
    train_graph = make_training_graph(subgraph, test_node, 5)
    print('train_graph has %d nodes and %d edges' %
          (train_graph.order(), train_graph.number_of_edges()))


    jaccard_scores = jaccard(train_graph, test_node, 5)
    print('\ntop jaccard scores for Bill Gates:')
    print(jaccard_scores)
    print('jaccard accuracy=%g' %
          evaluate([x[0] for x in jaccard_scores], subgraph))

    path_scores = path_score(train_graph, test_node, k=5, beta=.1)
    print('\ntop path scores for Bill Gates for beta=.1:')
    print(path_scores)
    print('path accuracy for beta .1=%g' %
          evaluate([x[0] for x in path_scores], subgraph))


if __name__ == '__main__':
    main()

