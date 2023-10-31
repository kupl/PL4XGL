from language import *
from connected import graph_is_connected, separate_a_graph
from synthesis.generalize import generalize 

#def synthesis_bu(data):
def learn_a_GDL_program(data):
  learned_tuples_set = set()
  data.default_score = float(len(data.target_labeled_graphs & data.train_graphs)/(len(data.train_graphs) + data.epsilon))
  #print("Default score : {}".format(data.default_score))
  #Given graph is connected  
  if graph_is_connected(data.graphs[data.target_graph],data):
    GDL_program = init_GDL_program_from_idx(data, data.target_graph)
    learned_GDL_program = generalize(GDL_program, data)
    score = eval_GDL_program_on_graphs_GC_Score(learned_GDL_program, data, data.target_labeled_graphs)
    chosen_graphs = eval_GDL_program_on_graphs_GC(learned_GDL_program, data)
    # The algorithm abandons the learned GDL program if the score is lower than the default score or the number of chosen graphs is 1.
    if (score < data.default_score * data.expected) or (len(chosen_graphs & data.train_graphs) == 1):
      print("This Learning failed!!")
    else:
      learned_tuple = (data.target_label, learned_GDL_program, score, frozenset(chosen_graphs))
      #learned_tuple = (learned_GDL_program, frozenset(chosen_graphs), score)
      learned_tuples_set.add(learned_tuple)
  #Given graph is not connected        
  else: 
    concrete_graphs_set = separate_a_graph(data.graphs[data.target_graph],data)
    for _, concrete_graph in enumerate(concrete_graphs_set):
      GDL_program = init_GDL_program_from_graph(data, concrete_graph)
      GDL_program = process_GDL_program_edges(GDL_program)
      learned_GDL_program = generalize(GDL_program, data)
      score = eval_GDL_program_on_graphs_GC_Score(learned_GDL_program, data, data.target_labeled_graphs)
      chosen_graphs = eval_GDL_program_on_graphs_GC(learned_GDL_program, data)   
      if (score < data.default_score * data.expected) or (len(chosen_graphs & data.train_graphs) == 1):
        #if (score < data.default_score * data.expected):
        print("This learning failed!!")
      else:
        #learned_tuple = (learned_GDL_program, frozenset(chosen_graphs), score)
        learned_tuple = (data.target_label, learned_GDL_program, score, frozenset(chosen_graphs))            
        learned_tuples_set.add(learned_tuple)
  return learned_tuples_set



#Assume the concrete graph is undirected but the following can also be used in directed graphs
def init_GDL_program_from_idx(data, graph_idx):
  GDL_program = GDL()
  GDL_program.nodeVars = []
  GDL_program.edgeVars = []
  node_abs_node_map = {}

  for i, val in enumerate(data.graphs[graph_idx][0]):
    node_feature = data.X_node[val]
    abs_node = {}
    for idx, feat_val in enumerate(node_feature):
      abs_node[idx] = (feat_val,feat_val) 
    GDL_program.nodeVars.append(abs_node)
    node_abs_node_map[val] = i
  for _, val in enumerate(data.graphs[graph_idx][1]):
    from_node = data.A[val][0]
    to_node = data.A[val][1]
    new_itv = {}
    edge_feature = data.X_edge[val]
    for idx, feat_val in enumerate(edge_feature):
      new_itv[idx] = (feat_val, feat_val)
    abs_edge = (new_itv, node_abs_node_map[from_node], node_abs_node_map[to_node])
    if to_node > from_node:
      GDL_program.edgeVars.append(abs_edge) 
  return GDL_program

#Assume the concrete graph is undirected but the following can also be used in directed graphs
def init_GDL_program_from_graph(data, concrete_graph):
  GDL_program = GDL()
  GDL_program.nodeVars = []
  GDL_program.edgeVars = []
  node_abs_node_map = {}

  for i, val in enumerate(concrete_graph[0]):
    node_feature = data.X_node[val]
    abs_node = {}
    for idx, feat_val in enumerate(node_feature):
      abs_node[idx] = (feat_val,feat_val) 
    GDL_program.nodeVars.append(abs_node)
    node_abs_node_map[val] = i
  for _, val in enumerate(concrete_graph[1]):
    from_node = data.A[val][0]
    to_node = data.A[val][1]
    new_itv = {}
    edge_feature = data.X_edge[val]
    for idx, feat_val in enumerate(edge_feature):
      new_itv[idx] = (feat_val, feat_val)
    abs_edge = (new_itv, node_abs_node_map[from_node], node_abs_node_map[to_node])
    if to_node > from_node:
      GDL_program.edgeVars.append(abs_edge)
  return GDL_program



