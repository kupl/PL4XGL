from language import *
from connected import *
import copy
import datetime


def generalize(GDL_program, data):
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
    if(elapsed > datetime.timedelta(seconds = data.timeLimit)):
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
    if(elapsed > datetime.timedelta(seconds = data.timeLimit)):
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
          if(elapsed > datetime.timedelta(seconds = data.timeLimit)):
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
          if(elapsed > datetime.timedelta(seconds = data.timeLimit)):
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
          if(elapsed > datetime.timedelta(seconds = data.timeLimit)):
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
          if(elapsed > datetime.timedelta(seconds = data.timeLimit)):
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
          if(elapsed > datetime.timedelta(seconds = data.timeLimit)):
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
          if(elapsed > datetime.timedelta(seconds = data.timeLimit)):
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
    if(elapsed > datetime.timedelta(seconds = data.timeLimit)):
      return (best_GDL_program, best_score)
    edge_idx = edge_idx - 1

  if flag == False : # no improvement
    return (best_GDL_program, best_score)

  else:
    return generalize_all(best_GDL_program, best_score, data)



