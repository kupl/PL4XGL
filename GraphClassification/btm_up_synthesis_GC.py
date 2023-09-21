from language import *
import datetime
import copy
import json
import sys
from connected import is_connected, graph_is_connected, separate_a_graph



def synthesis_bu(data):
  learned_tuples_set = set()
  data.default_score = float(len(data.target_labeled_graphs & data.train_graphs)/(len(data.train_graphs) + data.epsilon))
  #print("Default score : {}".format(data.default_score))
  #Given graph is connected  
  if graph_is_connected(data.graphs[data.target_graph],data):
    GDL_program = init_GDL_program_from_idx(data, data.target_graph)
    learned_GDL_program = synthesis(GDL_program, data)
    score = eval_GDL_program_on_graphs_GC_Score(learned_GDL_program, data, data.target_labeled_graphs)
    chosen_graphs = eval_GDL_program_on_graphs_GC(learned_GDL_program, data)
    # The algorithm abandons the learned GDL program if the score is lower than the default score or the number of chosen graphs is 1.
    if (score < data.default_score * data.expected) or (len(chosen_graphs & data.train_graphs) == 1):
      print("Learning failed!!")
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
      learned_GDL_program = synthesis(GDL_program, data)
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


def synthesis(GDL_program, data):
  # current GDL program and its score
  best_GDL_program = copy.deepcopy(GDL_program)
  best_score = eval_GDL_program_on_graphs_GC_Score(GDL_program, data, data.target_labeled_graphs)

  #best_GDL_program = process_unreachable_nodes(best_GDL_program)  
  # Remove edges unreachable nodes will be removed
  (best_GDL_program, best_score) = remove_edges(best_GDL_program, best_score, data) 


  best_GDL_program =  process_GDL_program_edges(best_GDL_program)
  (best_GDL_program, best_score) = generalize_edge(best_GDL_program, best_score, data) 
  (best_GDL_program, best_score) = generalize_node(best_GDL_program, best_score, data) 

  #additional refining for small dataset
  if len(data.train_graphs) < 1000:
    (best_GDL_program, best_score) = generalize_all(best_GDL_program, best_score, data) 
  # Remove unreachable nodes
  best_GDL_program = remove_unreachable_nodes(best_GDL_program)
  return best_GDL_program

def process_unreachable_nodes(GDL_program):
  node_indices_after = set()
  for _, (_, fr_node, to_node) in enumerate(GDL_program.edgeVars):
    node_indices_after.add(fr_node)
    node_indices_after.add(to_node)
  for index in range(len(GDL_program.nodeVars)):
    if not index in node_indices_after:
      GDL_program.nodeVars[index] = {}
  return GDL_program


def process_GDL_program_edges(GDL_program):
  current_abs_edges = copy.deepcopy(GDL_program.edgeVars)
  #print(len(GDL_program.nodeVars))
  #print(GDL_program.edgeVars)
  #print(current_abs_edges)
  new_edgeVars = [current_abs_edges[0]]

  reachable = set()
  reachable.add(current_abs_edges[0][1])
  reachable.add(current_abs_edges[0][2])
  candidates = set()
  for i in range(len(current_abs_edges)):
    candidates.add(i)
  candidates.remove(0)

  while (len(candidates) > 0):
    tmp_candidates = copy.deepcopy(candidates)
    for _, val in enumerate(tmp_candidates):
      if (current_abs_edges[val][1] in reachable) or (current_abs_edges[val][2] in reachable):
        reachable.add(current_abs_edges[val][1])
        reachable.add(current_abs_edges[val][2])
        new_edgeVars.append(current_abs_edges[val])
        candidates.remove(val)
    

  new_GDL_program = GDL ()
  new_GDL_program.nodeVars = copy.deepcopy(GDL_program.nodeVars)
  new_GDL_program.edgeVars = new_edgeVars 
  
  return new_GDL_program


def remove_edges(GDL_program, current_score, data) :

  best_GDL_program = GDL_program
  best_score = current_score
  edge_idx = len(GDL_program.edgeVars) - 1
  #remove edge
  while(edge_idx >= 0):
    new_GDL_program = copy.deepcopy(best_GDL_program)
    new_GDL_program.edgeVars.pop(edge_idx)
    if not (is_connected(new_GDL_program)) : 
      #print("This graph Is not connected")
      edge_idx = edge_idx - 1
      continue

    new_GDL_program = process_GDL_program_edges(new_GDL_program)
    new_score = eval_GDL_program_on_graphs_GC_Score(new_GDL_program, data, data.target_labeled_graphs)

    if (new_score >= best_score):
      best_GDL_program = new_GDL_program
      best_score = new_score
      #print()
      #print("NewAbsGraph")
      #print()
      #print("New Score : {}".format(new_score))

    edge_idx = edge_idx - 1
  return (best_GDL_program, best_score)
 



def generalize_edge(GDL_program, current_score, data) :
  best_GDL_program = GDL_program
  best_score = current_score
  edge_idx = len(best_GDL_program.edgeVars) - 1
  while(edge_idx >= 0):
    new_GDL_program = copy.deepcopy(best_GDL_program)
    new_itv = {}
    new_from = new_GDL_program.edgeVars[edge_idx][1]
    new_to = new_GDL_program.edgeVars[edge_idx][2] 
    new_GDL_program.edgeVars[edge_idx] = (new_itv, new_from, new_to)
    start = datetime.datetime.now()
    new_score = eval_GDL_program_on_graphs_GC_Score(new_GDL_program, data, data.target_labeled_graphs)
    if (new_score >= best_score):
      best_GDL_program = new_GDL_program
      best_score = new_score
    edge_idx = edge_idx - 1
    finish = datetime.datetime.now() 
    elapsed = finish - start
    if(elapsed > datetime.timedelta(seconds=10)):
      break
  return (best_GDL_program, best_score)



def generalize_node(GDL_program, current_score, data) :
  best_GDL_program = GDL_program
  best_score = current_score
  node_idx = len(best_GDL_program.nodeVars) - 1
  while(node_idx >= 0):
    new_GDL_program = copy.deepcopy(best_GDL_program)
    new_GDL_program.nodeVars[node_idx] = {}
    start = datetime.datetime.now()
    new_score = eval_GDL_program_on_graphs_GC_Score(new_GDL_program, data, data.target_labeled_graphs)

    if (new_score >= best_score):
      best_GDL_program = new_GDL_program
      best_score = new_score

    node_idx = node_idx - 1
    finish = datetime.datetime.now() 
    elapsed = finish - start
    if(elapsed > datetime.timedelta(seconds=10)):
      break
  return (best_GDL_program, best_score)



def generalize_all(GDL_program, current_score, data) :
  best_GDL_program = GDL_program
  best_score = current_score
  current_GDL_program = GDL_program
  flag = False
  #start_0 = datetime.datetime.now()
  #print("Widening node intervals")
  for node_idx in range(len(GDL_program.nodeVars)):
    itvs = current_GDL_program.nodeVars[node_idx]
    if itvs == {}:
      continue
    else:
      for _, feat_idx in enumerate(itvs):
        (a, b) = itvs[feat_idx]
        if a != -99 and b != 99:
          new_GDL_program = copy.deepcopy(current_GDL_program)
          new_itvs = copy.deepcopy(itvs)
          new_itvs[feat_idx] = (a,99)
          new_GDL_program.nodeVars[node_idx] = new_itvs
          
          start = datetime.datetime.now() 
          new_score = eval_GDL_program_on_graphs_GC_Score(new_GDL_program, data, data.target_labeled_graphs)

          if (new_score >= best_score):
            flag = True
            best_GDL_program = new_GDL_program
            best_score = new_score
          finish = datetime.datetime.now() 
          elapsed = finish - start
          if(elapsed > datetime.timedelta(seconds=10)):
            return (best_GDL_program, best_score)

          new_GDL_program = copy.deepcopy(current_GDL_program)
          new_itvs = copy.deepcopy(itvs)
          new_itvs[feat_idx] = (-99,b)
          new_GDL_program.nodeVars[node_idx] = new_itvs

          start = datetime.datetime.now() 
          new_score = eval_GDL_program_on_graphs_GC_Score(new_GDL_program, data, data.target_labeled_graphs)

          if (new_score >= best_score):
            flag = True
            best_GDL_program = new_GDL_program
            best_score = new_score
          finish = datetime.datetime.now() 
          elapsed = finish - start
          if(elapsed > datetime.timedelta(seconds=10)):
            return (best_GDL_program, best_score)


        elif (a != -99 and b == 99) or (a == -99 and b != 99):
          new_GDL_program = copy.deepcopy(current_GDL_program)
          new_itvs = copy.deepcopy(itvs)
          del new_itvs[feat_idx]
          #new_itvs[feat_idx] = (-99,99)
          new_GDL_program.nodeVars[node_idx] = new_itvs

          start = datetime.datetime.now() 
          new_score = eval_GDL_program_on_graphs_GC_Score(new_GDL_program, data, data.target_labeled_graphs)
                    
          if (new_score >= best_score):
            flag = True
            best_GDL_program = new_GDL_program
            best_score = new_score
          finish = datetime.datetime.now() 
          elapsed = finish - start
          if(elapsed > datetime.timedelta(seconds=10)):
            return (best_GDL_program, best_score)

        else:
          continue

  #print("Widening edge intervals")
  for edge_idx in range(len(GDL_program.edgeVars)):
    (itvs, p, q) = current_GDL_program.edgeVars[edge_idx]
    if itvs == {}:
      continue
    else:
      for _, feat_idx in enumerate(itvs):
        (a, b) = itvs[feat_idx]
        if a != -99 and b != 99:
          new_GDL_program = copy.deepcopy(current_GDL_program)
          new_itvs = copy.deepcopy(itvs)
          new_itvs[feat_idx] = (a,99)
          new_GDL_program.edgeVars[edge_idx] = (new_itvs, p, q)

          start = datetime.datetime.now() 
          new_score = eval_GDL_program_on_graphs_GC_Score(new_GDL_program, data, data.target_labeled_graphs)
          
          if (new_score >= best_score):
            flag = True
            best_GDL_program = new_GDL_program
            best_score = new_score
          finish = datetime.datetime.now() 
          elapsed = finish - start
          if(elapsed > datetime.timedelta(seconds=10)):
            return (best_GDL_program, best_score)

          new_GDL_program = copy.deepcopy(current_GDL_program)
          new_itvs = copy.deepcopy(itvs)
          new_itvs[feat_idx] = (-99,b)
          new_GDL_program.edgeVars[edge_idx] = (new_itvs, p, q)

          start = datetime.datetime.now() 
          new_score = eval_GDL_program_on_graphs_GC_Score(new_GDL_program, data, data.target_labeled_graphs)
          
          if (new_score >= best_score):
            flag = True
            best_GDL_program = new_GDL_program
            best_score = new_score
          finish = datetime.datetime.now() 
          elapsed = finish - start
          if(elapsed > datetime.timedelta(seconds=10)):
            return (best_GDL_program, best_score)
          
        elif (a != -99 and b == 99) or (a == -99 and b != 99):
          new_GDL_program = copy.deepcopy(current_GDL_program)
          new_itvs = copy.deepcopy(itvs)
          del new_itvs[feat_idx]
          #new_itvs[feat_idx] = (-99,99)
          new_GDL_program.edgeVars[edge_idx] = (new_itvs, p, q)

          start = datetime.datetime.now() 
          new_score = eval_GDL_program_on_graphs_GC_Score(new_GDL_program, data, data.target_labeled_graphs)
          
          if (new_score >= best_score):
            flag = True
            best_GDL_program = new_GDL_program
            best_score = new_score
          finish = datetime.datetime.now() 
          elapsed = finish - start
          if(elapsed > datetime.timedelta(seconds=10)):
            return (best_GDL_program, best_score)
        else:
          continue

  #print("Removing edge")
  edge_idx = len(GDL_program.edgeVars) - 1
  while(edge_idx >= 0):
    new_GDL_program = copy.deepcopy(current_GDL_program)
    new_GDL_program.edgeVars.pop(edge_idx)
    if not (is_connected(new_GDL_program)) : 
      edge_idx = edge_idx - 1
      continue
    new_GDL_program =  process_GDL_program_edges(new_GDL_program)
    start = datetime.datetime.now() 
    new_score = eval_GDL_program_on_graphs_GC_Score(new_GDL_program, data, data.target_labeled_graphs)
    if (new_score >= best_score):
      flag = True
      #print("edge_idx : {}".format(edge_idx))
      best_GDL_program = new_GDL_program
      best_score = new_score
    finish = datetime.datetime.now() 
    elapsed = finish - start
    if(elapsed > datetime.timedelta(seconds=10)):
      return (best_GDL_program, best_score)
    edge_idx = edge_idx - 1

  if flag == False : # no improvement
    return (best_GDL_program, best_score)

  else:
    return generalize_all(best_GDL_program, best_score, data)



