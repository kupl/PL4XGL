import copy
import sys

class Graph:
  def __init__(self):
    self.Nodes = set()
    self.Edges = {}

  idx_node_map = {}
  node_idx_map = {}


  def takeNodes (self, nodes):
    nodes = list(nodes)
    nodes.sort()

    for i in range(len(nodes)):
      self.idx_node_map[nodes[i]] = i
      self.node_idx_map[i] = nodes[i]


    for i in range(len(nodes)):
      self.Nodes.add(self.idx_node_map[nodes[i]])
      self.Edges[self.idx_node_map[nodes[i]]] = set()

  def addEdge(self, fr, to):
    if not (self.idx_node_map[fr] in self.Edges):
      self.idx_node_map[fr] = set()
    if not (self.idx_node_map[to] in self.Edges):
      self.idx_node_map[to] = set()

    self.Edges[self.idx_node_map[fr]].add(self.idx_node_map[to])
    self.Edges[self.idx_node_map[to]].add(self.idx_node_map[fr])



def DFS(src, edges):
  visited_nodes = set([src])
  #my_edges = set()
  for i in range(len(edges)):
    adj_nodes = set()
    for _,node in enumerate(visited_nodes):
      for _, adj_node in enumerate(edges[node]):
        adj_nodes = adj_nodes | edges[node]
    visited_nodes = visited_nodes | adj_nodes
  return visited_nodes



def my_DFS(src, edges):
  visited_nodes = set([src])
  my_edges = set()
  for i in range(len(edges)):
    adj_nodes = set()
    for _,node in enumerate(visited_nodes):
      for _, adj_node in enumerate(edges[node]):
        adj_nodes.add(adj_node)
        my_edges.add((node,adj_node))
      #adj_nodes = adj_nodes | edges[node]
    visited_nodes = visited_nodes | adj_nodes
  return (visited_nodes, my_edges)


def is_connected(GDL_program):
  edges = GDL_program.edgeVars

  nodes = set()
  for _, (_, fr, to) in enumerate(edges):
    nodes.add(fr)
    nodes.add(to)
  graph = Graph()
  graph.takeNodes(nodes)

  for _, (_, fr, to) in enumerate(edges):
    graph.addEdge(fr, to)

  return IsConnected(graph)


def IsConnected(graph):
  nodes = graph.Nodes
  edges = graph.Edges

  visited_nodes_len = len(DFS(0, edges))
  #print(visited_nodes_len)
  #print(len(nodes))
  return (visited_nodes_len == len(nodes) )



def graph_is_connected(graph, data):
  my_graph = Graph()
  edges = graph[1]

  nodes = set()
  for _, edge_idx in enumerate(edges):
    (fr, to) = data.A[edge_idx]
    nodes.add(fr)
    nodes.add(to)
  my_graph.takeNodes(nodes)
  for _, edge_idx in enumerate(edges):
    (fr, to) = data.A[edge_idx]
    my_graph.addEdge(fr, to)
  return IsConnected(my_graph)


'''
def separate_graph(graph, A):
  nodes = graph.Nodes
  edges = graph.Edges
  separated_graph_set = []
  my_nodes = copy.deepcopy(nodes)
  while len(my_nodes) > 0:
    subgraph = [[],[]]
    src = my_nodes.pop()
    (reachable_nodes, my_edges) = my_DFS(src, edges)
    for _, node_idx in enumerate(reachable_nodes):
      subgraph[0].append(graph.node_idx_map[node_idx])
    for _, (fr, to) in enumerate(my_edges):
      fr_node = graph.node_idx_map[fr]
      to_node = graph.node_idx_map[to]
      subgraph[1].append(A.index((fr_node,to_node)))
    #print(subgraph)
    my_nodes = my_nodes - reachable_nodes
    #sys.exit()
    separated_graph_set.append(subgraph)
  return separated_graph_set
'''


def separate_a_graph(graph, data):
  separated_graph_set = set()

  my_graph = Graph()
  edges = graph[1]
  nodes = set()
  for _, edge_idx in enumerate(edges):
    (fr, to) = data.A[edge_idx]
    nodes.add(fr)
    nodes.add(to)
  my_graph.takeNodes(nodes)
  for _, edge_idx in enumerate(edges):
    (fr, to) = data.A[edge_idx]
    my_graph.addEdge(fr, to)

  separated_graph_set = separate_graph(my_graph, data.A)
  #print(len(separated_graph_set))
  #sys.exit()
  return separated_graph_set

