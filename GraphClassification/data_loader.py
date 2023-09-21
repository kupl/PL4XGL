import pickle
import sys

class Data:
  graph_to_label = {} 
  graphs = [] 
  train_graphs = set()
  val_graphs = set()
  test_graphs = set()
  A = []
  X_node = {}
  X_edge = {}
  chosen_depth = 1
  succ_node_to_nodes = {}
  pred_node_to_nodes = {}
  nodes_to_edge = {}

  def __init__(self):
    self.left_graphs = set()
    self.target_labeled_graphs = set()


def load_MUTAG():
  data = Data()

  with open("datasets/MUTAG/tr.pickle", 'rb') as f:
    train_graphs = pickle.load(f)

  with open("datasets/MUTAG/va.pickle", 'rb') as f:
    val_graphs = pickle.load(f)

  with open("datasets/MUTAG/te.pickle", 'rb') as f:
    test_graphs = pickle.load(f)


  graph_to_edges = {}
  graph_to_nodes = {}
  node_to_graph = {}

  with open("datasets/MUTAG/MUTAG_graph_indicator.txt") as file:
    i = 0 
    for line in file.readlines():
      graph_idx = line.strip()
      idx = int(graph_idx) - 1
      node_to_graph[i] = idx
      if not idx in graph_to_nodes:
        graph_to_nodes[idx] = []
      graph_to_nodes[idx].append(i)
      graph_to_edges[idx] = []
      i = i+1

  A = []
  with open("datasets/MUTAG/MUTAG_A.txt") as file:
    i = 0
    j = 0
    for line in file.readlines():
      edge = line.strip().split(', ')
      fr_node = int(edge[0]) - 1
      to_node = int(edge[1]) - 1
      A.append((fr_node, to_node))
      if fr_node in graph_to_nodes[j]:
        graph_to_edges[j].append(i)
      elif fr_node in graph_to_nodes[j+1]:
        j = j + 1
        graph_to_edges[j] = [i]
      i = i + 1
  
  label_to_graphs = {}
  graph_to_label = {}
  with open("datasets/MUTAG/MUTAG_graph_labels.txt") as file:
    i = 0 
    for line in file.readlines():
      label = line.strip()
      label = int(label)
      graph_to_label[i] = label
      if not label in label_to_graphs:
        label_to_graphs[label] = set()
      label_to_graphs[label].add(i)
      i = i+1
  
  node_to_label = {}
  with open("datasets/MUTAG/MUTAG_node_labels.txt") as file:
    i = 0 
    for line in file.readlines():
      label = line.strip()
      int_label = int(label) 
      node_to_label[i] = int_label
      i = i+1

  X_node = []
  for i in range(len(node_to_label)):
    X_node.append([node_to_label[i]])

  edge_to_label = {}
  with open("datasets/MUTAG/MUTAG_edge_labels.txt") as file:
    i = 0 
    for line in file.readlines():
      label = line.strip()
      int_label = int(label)
      edge_to_label[i] = int_label
      i = i+1

  X_edge = []
  for i in range(len(edge_to_label)):
    X_edge.append([edge_to_label[i]])

  labeled_graphs = set()
  for i, val in enumerate(graph_to_label):
    #if graph_to_label[i] == -1:
    if graph_to_label[i] == 1:
      labeled_graphs.add(i)

  graphs = []
  graph_indices = set()
  for i in range(len(graph_to_label)):
    graph_indices.add(i)
    new_graph = [] 
    new_graph.append(graph_to_nodes[i])
    new_graph.append(graph_to_edges[i])
    graphs.append(new_graph)  


  succ_node_to_nodes = {}
  pred_node_to_nodes = {}
  nodes_to_edge = {}

  for idx, val in enumerate(A):
    fr_node = val[0]
    to_node = val[1]
    nodes_to_edge[(fr_node, to_node)] = idx
    if not fr_node in succ_node_to_nodes:
      succ_node_to_nodes[fr_node] = set()
    if not to_node in pred_node_to_nodes:
      pred_node_to_nodes[to_node] = set()
    succ_node_to_nodes[fr_node].add((idx, to_node))
    pred_node_to_nodes[to_node].add((idx, fr_node))

 

  data.train_graphs = train_graphs
  data.val_graphs = val_graphs
  data.test_graphs = test_graphs
  data.graph_indices = graph_indices
  data.graphs = graphs
  data.X_edge = X_edge
  data.X_node = X_node
  data.A = A
  data.graph_to_label = graph_to_label
  data.label_to_graphs = label_to_graphs
  data.succ_node_to_nodes = succ_node_to_nodes
  data.pred_node_to_nodes = pred_node_to_nodes
  data.nodes_to_edge = nodes_to_edge
  data.epsilon = 0.1
  data.expected = 1.2
  return data



def load_BBBP():
  data = Data()

  with open("datasets/BBBP/tr.pickle", 'rb') as f:
    train_graphs = pickle.load(f)

  with open("datasets/BBBP/va.pickle", 'rb') as f:
    val_graphs = pickle.load(f)

  with open("datasets/BBBP/te.pickle", 'rb') as f:
    test_graphs = pickle.load(f)

  with open("datasets/BBBP/graph_to_label_bbbp.pickle", 'rb') as f:
    graph_to_label = pickle.load(f)

  with open("datasets/BBBP/X_node_bbbp.pickle", 'rb') as f:
    X_node = pickle.load(f)

  with open("datasets/BBBP/X_edge_bbbp.pickle", 'rb') as f:
    X_edge = pickle.load(f)

  with open("datasets/BBBP/new_A_bbbp.pickle", 'rb') as f:
    A = pickle.load(f)

  with open("datasets/BBBP/graphs_bbbp.pickle", 'rb') as f:
    graphs = pickle.load(f)



  new_graphs = []
  for i, val in enumerate(graphs):
    new_graph = []
    nodes = set()
    for _, edge_idx in enumerate(val[1]):
      (fr, to) = A[edge_idx]
      nodes.add(fr)
      nodes.add(to)
    nodes= list(nodes)
    new_graph.append(nodes)
    new_graph.append(val[1])
    new_graphs.append(new_graph)
  graphs = new_graphs



  label_to_graphs = {} 
  label_to_graphs[0] = set()
  label_to_graphs[1] = set()
  graph_indices = set()
  new_graph_to_label = {}

  for i, val in enumerate(graph_to_label):
    graph_indices.add(i)
    if graph_to_label[i] == 1:
      label_to_graphs[1].add(i)
      new_graph_to_label[i] = 1
    elif graph_to_label[i] == -1:
      label_to_graphs[0].add(i)
      new_graph_to_label[i] = 0 
    else:
      print("Cannot be happened")
      raise ValueError


 
  succ_node_to_nodes = {}
  pred_node_to_nodes = {}
  nodes_to_edge = {}

  for idx, val in enumerate(A):
    fr_node = val[0]
    to_node = val[1]
    nodes_to_edge[(fr_node, to_node)] = idx
    if not fr_node in succ_node_to_nodes:
      succ_node_to_nodes[fr_node] = set()
    if not to_node in pred_node_to_nodes:
      pred_node_to_nodes[to_node] = set()
    succ_node_to_nodes[fr_node].add((idx, to_node))
    pred_node_to_nodes[to_node].add((idx, fr_node))

 
  data.train_graphs = train_graphs
  data.val_graphs = val_graphs
  data.test_graphs = test_graphs
  data.graph_indices = graph_indices
  data.graphs = graphs
  data.X_edge = X_edge
  data.X_node = X_node
  data.A = A
  #data.graph_to_label = graph_to_label
  data.graph_to_label = new_graph_to_label
  data.label_to_graphs = label_to_graphs
  data.succ_node_to_nodes = succ_node_to_nodes
  data.pred_node_to_nodes = pred_node_to_nodes
  data.nodes_to_edge = nodes_to_edge
  data.epsilon = 0.1
  data.expected = 1.2
  return data
  #BBBBP



def load_BACE():
  data = Data()

  with open("datasets/BACE/tr.pickle", 'rb') as f:
    train_graphs = pickle.load(f)

  with open("datasets/BACE/va.pickle", 'rb') as f:
    val_graphs = pickle.load(f)

  with open("datasets/BACE/te.pickle", 'rb') as f:
    test_graphs = pickle.load(f)

  with open("datasets/BACE/graph_to_label_bace.pickle", 'rb') as f:
    graph_to_label = pickle.load(f)

  with open("datasets/BACE/X_node_bace.pickle", 'rb') as f:
    X_node = pickle.load(f)

  with open("datasets/BACE/X_edge_bace.pickle", 'rb') as f:
    X_edge = pickle.load(f)

  with open("datasets/BACE/new_A_bace.pickle", 'rb') as f:
    A = pickle.load(f)

  with open("datasets/BACE/graphs_bace.pickle", 'rb') as f:
    graphs = pickle.load(f)



  new_graphs = []
  for i, val in enumerate(graphs):
    new_graph = []
    nodes = set()
    for _, edge_idx in enumerate(val[1]):
      (fr, to) = A[edge_idx]
      nodes.add(fr)
      nodes.add(to)
    nodes= list(nodes)
    new_graph.append(nodes)
    new_graph.append(val[1])
    new_graphs.append(new_graph)
  graphs = new_graphs



  label_to_graphs = {} 
  label_to_graphs[0] = set()
  label_to_graphs[1] = set()
  graph_indices = set()
  new_graph_to_label = {}

  for i, val in enumerate(graph_to_label):
    graph_indices.add(i)
    if graph_to_label[i] == 1:
      label_to_graphs[1].add(i)
      new_graph_to_label[i] = 1
    elif graph_to_label[i] == 0:
      label_to_graphs[0].add(i)
      new_graph_to_label[i] = 0 
    else:
      print("Cannot be happened")
      raise ValueError


 
  succ_node_to_nodes = {}
  pred_node_to_nodes = {}
  nodes_to_edge = {}

  for idx, val in enumerate(A):
    fr_node = val[0]
    to_node = val[1]
    nodes_to_edge[(fr_node, to_node)] = idx
    if not fr_node in succ_node_to_nodes:
      succ_node_to_nodes[fr_node] = set()
    if not to_node in pred_node_to_nodes:
      pred_node_to_nodes[to_node] = set()
    succ_node_to_nodes[fr_node].add((idx, to_node))
    pred_node_to_nodes[to_node].add((idx, fr_node))

 
  data.train_graphs = train_graphs
  data.val_graphs = val_graphs
  data.test_graphs = test_graphs
  data.graph_indices = graph_indices
  data.graphs = graphs
  data.X_edge = X_edge
  data.X_node = X_node
  data.A = A
  data.graph_to_label = graph_to_label
  data.label_to_graphs = label_to_graphs
  data.succ_node_to_nodes = succ_node_to_nodes
  data.pred_node_to_nodes = pred_node_to_nodes
  data.nodes_to_edge = nodes_to_edge
  data.epsilon = 1
  data.expected = 1.2
  return data
















