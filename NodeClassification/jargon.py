#language
class Sentence:
  absList = []
  root = 0
  def __init__(self):
    self.absList = []
    self.root = 0

def filter_eval_sentence(sentence, succ_node_to_nodes, pred_node_to_nodes, X_arr, filtered_nodes):

  nodes = filter_process_target(sentence, X_arr, filtered_nodes) 
  
  node_succ_nodes = {}
  node_pred_nodes = {}
  for i,val in enumerate(nodes):
    node_succ_nodes[val] = succ_node_to_nodes[val]
    node_pred_nodes[val] = pred_node_to_nodes[val]
  nodes = process_succs(sentence, X_arr, nodes, node_succ_nodes, succ_node_to_nodes, sentence.root+1)
  nodes = process_preds(sentence, X_arr, nodes, node_pred_nodes, pred_node_to_nodes, sentence.root-1)
  
  nodes = filter_redundant(sentence, X_arr, nodes, succ_node_to_nodes, pred_node_to_nodes)
  
  return nodes

#evaluate target node 
def filter_process_target(sentence, X_arr, filtered_nodes):
  abs_node = sentence.absList[sentence.root]
  nodes = filtered_nodes
  nodes = process_abstract_node(abs_node, nodes, X_arr)
  return nodes




#evaluate a sentence
def eval_sentence(sentence, succ_node_to_nodes, pred_node_to_nodes, X_arr):

  nodes = process_target(sentence, X_arr) 
  
  node_succ_nodes = {}
  node_pred_nodes = {}
  for i,val in enumerate(nodes):
    node_succ_nodes[val] = succ_node_to_nodes[val]
    node_pred_nodes[val] = pred_node_to_nodes[val]
  nodes = process_succs(sentence, X_arr, nodes, node_succ_nodes, succ_node_to_nodes, sentence.root+1)
  nodes = process_preds(sentence, X_arr, nodes, node_pred_nodes, pred_node_to_nodes, sentence.root-1)



  nodes = filter_redundant(sentence, X_arr, nodes, succ_node_to_nodes, pred_node_to_nodes)
  return nodes



def filter_redundant(sentence, X_arr, nodes, succ_node_to_nodes, pred_node_to_nodes):
  if len(sentence.absList) < 3:
    return nodes
  elif len(sentence.absList) == 3:
    if sentence.root == 1:
      filtered_nodes = set()
      for _, val in enumerate(nodes):
        if exist_path(sentence, X_arr, val, succ_node_to_nodes, pred_node_to_nodes):
          filtered_nodes.add(val)
      return filtered_nodes
    #elif root = 1:
    elif sentence.root == 0:#root = 2
      filtered_nodes = set()
      for _, val in enumerate(nodes):
        if exist_path0(sentence, X_arr, val, succ_node_to_nodes, pred_node_to_nodes):
          filtered_nodes.add(val)
      return filtered_nodes
    elif sentence.root == 2:
      filtered_nodes = set()
      for _, val in enumerate(nodes):
        if exist_path2(sentence, X_arr, val, succ_node_to_nodes, pred_node_to_nodes):
          filtered_nodes.add(val)
      return filtered_nodes
  else:
    raise("Error : The length of sentence is greater than 3")
    return nodes



def exist_path(sentence, X_arr, val, node_succ_nodes, node_pred_nodes):
  #if val == 248:
  #  print(val)
  
  pred_nodes = node_pred_nodes[val]
  pred_nodes = process_abstract_node(sentence.absList[0], pred_nodes, X_arr)
  if len(pred_nodes) > 1: 
    return True
  succ_nodes = node_succ_nodes[val]
  succ_nodes = process_abstract_node(sentence.absList[2], succ_nodes, X_arr)
  if len(succ_nodes) > 1:
    return True
  
  if len(pred_nodes - succ_nodes) == 0:
    return False
  else:
    return True



def exist_path0(sentence, X_arr, val,succ_node_to_nodes, pred_node_to_nodes):
  succ_nodes = succ_node_to_nodes[val]
  succ_nodes = process_abstract_node(sentence.absList[1], succ_nodes, X_arr)

  succ_succ_nodes = set() 
  for _, node in enumerate(succ_nodes):
    succ_succ_nodes = succ_succ_nodes | succ_node_to_nodes[node]
  succ_succ_nodes = process_abstract_node(sentence.absList[2], succ_succ_nodes, X_arr)
  if len(succ_succ_nodes - set([val])) >= 1:
    return True
  
  else:
    return False 



def exist_path2(sentence, X_arr, val,succ_node_to_nodes, pred_node_to_nodes):
  pred_nodes = pred_node_to_nodes[val]
  pred_nodes = process_abstract_node(sentence.absList[1], pred_nodes, X_arr)

  pred_pred_nodes = set() 
  for _, node in enumerate(pred_nodes):
    pred_pred_nodes = pred_pred_nodes | pred_node_to_nodes[node]
  pred_pred_nodes = process_abstract_node(sentence.absList[0], pred_pred_nodes, X_arr)
  if len(pred_pred_nodes - set([val])) >= 1:
    return True
  
  else:
    return False 





#evaluate a node
def process_abstract_node(abs_node, nodes, X_arr):
  filtered_nodes = set()
  if len(abs_node) == 0:
    return nodes
  for i, candidate_node in enumerate(nodes):
    flag = True
    for j, index in enumerate(abs_node):
      (bot,top) = abs_node[index]
      if X_arr[candidate_node][index] < bot or top < X_arr[candidate_node][index]:
        flag = False
        break
    if flag == True:
      filtered_nodes.add(candidate_node)
  return filtered_nodes



#evaluate target node 
def process_target(sentence, X_arr):
  abs_node = sentence.absList[sentence.root]
  nodes = set()
  for i, val in enumerate(X_arr):
    nodes.add(i)
  nodes = process_abstract_node(abs_node, nodes, X_arr)
  return nodes


#evaluate successor nodes 
def process_succs(sentence, X_arr, nodes, node_succ_nodes, node_to_nodes, idx):
  if idx == len(sentence.absList):
    return nodes
  abs_node = sentence.absList[idx] # (bot,top)
  filtered_nodes = set ()
  new_node_succ_nodes = {}
  for i, val in enumerate(nodes):
    succ_nodes = process_abstract_node(abs_node, node_succ_nodes[val], X_arr)
    if len(succ_nodes) > 0:
      new_node_succ_nodes[val] = set()
      filtered_nodes.add(val)
      for j, myval in enumerate(succ_nodes):
        new_node_succ_nodes[val] = new_node_succ_nodes[val] | node_to_nodes[myval]
  return process_succs(sentence, X_arr, filtered_nodes, new_node_succ_nodes, node_to_nodes, idx+1)


#evaluate predecessor nodes 
def process_preds(sentence, X_arr, nodes, node_pred_nodes, node_to_nodes, idx):
  if idx < 0:
    return nodes
  abs_node = sentence.absList[idx] # (bot,top)
  filtered_nodes = set ()
  new_node_pred_nodes = {}
  for i, val in enumerate(nodes):
    pred_nodes = process_abstract_node(abs_node, node_pred_nodes[val], X_arr)
    if len(pred_nodes) > 0:
      new_node_pred_nodes[val] = set()
      filtered_nodes.add(val)
      for j, myval in enumerate(pred_nodes):
        new_node_pred_nodes[val] = new_node_pred_nodes[val] | node_to_nodes[myval]

  return process_preds(sentence, X_arr, filtered_nodes, new_node_pred_nodes, node_to_nodes, idx-1)

