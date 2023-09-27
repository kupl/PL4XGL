import copy
import sys 


class Graph:
  def __init__(self):
    self.Nodes = set()
    self.Edges = {}
    self.Idx_node_map = {}


def my_connect(abs_graph):
  edges = abs_graph.absEdges
 
  nodes = set()  
  for _, (_, fr, to) in enumerate(edges):
    nodes.add(fr)
    nodes.add(to)
  graph = Graph()
  takeNodes(graph, nodes) 

  for _, (_, fr, to) in enumerate(edges):
    addEdge(graph, fr, to)

  return IsConnected(graph)

def takeNodes (graph, nodes):
  nodes = list(nodes)
  nodes.sort()
  for i in range(len(nodes)):
    graph.Idx_node_map[nodes[i]] = i

  for i in range(len(nodes)):
    graph.Nodes.add(graph.Idx_node_map[nodes[i]])
    graph.Edges[graph.Idx_node_map[nodes[i]]] = set()

def addEdge(graph, fr, to):
  if not (graph.Idx_node_map[fr] in graph.Edges):
    graph.Idx_node_map[fr] = set()
  if not (graph.Idx_node_map[to] in graph.Edges):
    graph.Idx_node_map[to] = set()

  graph.Edges[graph.Idx_node_map[fr]].add(graph.Idx_node_map[to])
  graph.Edges[graph.Idx_node_map[to]].add(graph.Idx_node_map[fr])


def takeNodes (graph, nodes):
  nodes = list(nodes)
  nodes.sort()
  for i in range(len(nodes)):
    graph.Idx_node_map[nodes[i]] = i

  for i in range(len(nodes)):
    graph.Nodes.add(graph.Idx_node_map[nodes[i]])
    graph.Edges[graph.Idx_node_map[nodes[i]]] = set()

def addEdge(graph, fr, to):
  if not (graph.Idx_node_map[fr] in graph.Edges):
    graph.Idx_node_map[fr] = set()
  if not (graph.Idx_node_map[to] in graph.Edges):
    graph.Idx_node_map[to] = set()

  graph.Edges[graph.Idx_node_map[fr]].add(graph.Idx_node_map[to])
  graph.Edges[graph.Idx_node_map[to]].add(graph.Idx_node_map[fr])


def DFS(src, edges):
  visited_nodes = set([src])
  for i in range(len(edges)):
    adj_nodes = set()
    for _,node in enumerate(visited_nodes):
      adj_nodes = adj_nodes | edges[node]
    visited_nodes = visited_nodes | adj_nodes
  return len(visited_nodes)

def IsConnected(graph):
  nodes = graph.Nodes
  edges = graph.Edges

  visited_nodes_len = DFS(0, edges)
  return (visited_nodes_len == len(nodes) )


