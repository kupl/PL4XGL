import copy

class Undefined(Exception):
    pass


class GDL:
  def __init__(self):
    self.nodeVars = []
    self.edgeVars = []


def eval_node_var(node_var, nodes, X_node):
  filtered_nodes = set()
  if len(node_var) == 0:
    return nodes
  for _, node in enumerate(nodes):
    flag = True
    for _, feat_idx in enumerate(node_var):
      (bot, top) = node_var[feat_idx]

      if X_node[node][feat_idx] < bot or top < X_node[node][feat_idx]:
        flag = False
        break
    if flag == True:
      filtered_nodes.add(node)
  return filtered_nodes


def eval_edge_var(edge_var, edges, X_edge):
  filtered_edges = set()
  if len(edge_var) == 0:
    return edges
  (itvs, p, q) = edge_var 
  for _, edge in enumerate(edges):
    flag = True
    for _, feat_idx in enumerate(itvs):
      (bot, top) = itvs[feat_idx]
      if X_edge[edge][feat_idx] < bot or top < X_edge[edge][feat_idx]:
        flag = False
        break
    if flag == True:
      filtered_edges.add(edge)
  return filtered_edges

def GDL_program_size (GDL_program):
  size = 0
  size = size + len(GDL_program.nodeVars)
  size = size + len(GDL_program.edgeVars)
  return size


def filter_eval_GDL_program_NC_DFS(GDL_program, my_maps, filtered_nodes):
  candidate_nodes = eval_node_var(GDL_program.nodeVars[0], my_maps.nodes, my_maps.X_node) & filtered_nodes
  chosen_nodes = set()
  for _, node in enumerate(candidate_nodes):
    if exist_subgraph_NC_DFS([[node],[]], [[0],[]], GDL_program, my_maps, 0) == 0:
      chosen_nodes.add(node)

  return chosen_nodes 


#node_projection
def eval_GDL_program_NC_DFS(GDL_program, my_maps):
  candidate_nodes = eval_node_var(GDL_program.nodeVars[0], my_maps.nodes, my_maps.X_node)
  chosen_nodes = set()
  for _, node in enumerate(candidate_nodes):
    if exist_subgraph_NC_DFS([[node],[]], [[0],[]], GDL_program, my_maps, 0) == 0:
      chosen_nodes.add(node)

  return chosen_nodes 


def exist_subgraph_NC_DFS(subgraph, sub_GDL_program, GDL_program, my_maps, edge_var_idx):
  if len(GDL_program.edgeVars) == edge_var_idx:
    return 0
  target_edge_var = GDL_program.edgeVars[edge_var_idx]
  new_sub_GDL_program = copy.deepcopy(sub_GDL_program)
  (new_sub_GDL_program, case) = get_edge_var_case_and_update_sub_GDL_program(new_sub_GDL_program, target_edge_var)
  if case == 2:
    #Need check
    node_var_fr = target_edge_var[1]
    node_var_to = target_edge_var[2]
    fr_con = subgraph[0][node_var_fr]
    to_con = subgraph[0][node_var_to]
    if to_con in my_maps.succ_node_to_nodes[fr_con]: 
      con_edge = (fr_con, to_con)
      new_subgraph = copy.deepcopy(subgraph)
      new_subgraph[1].append(con_edge)
      if exist_subgraph_NC_DFS(new_subgraph, new_sub_GDL_program, GDL_program, my_maps, edge_var_idx + 1) == 0:
        return 0 

  elif case == 1:
    #new_fr
    node_var_fr = target_edge_var[1] # checkthis
    node_var_to = target_edge_var[2]
    #to_con = node_var_idx_to_concrete_node[node_var_to]
    #print("Subgraph : {}".format(subgraph))
    #print("AbsNode Fr {}".format(node_var_fr))
    #print("AbsNode To {}".format(node_var_to))
    #print(subgraph[0][node_var_to])
    #print(subgraph[0])
    #print(subgraph[0][node_var_to])
    to_con = subgraph[0][node_var_to]
    candidate_fr_nodes = my_maps.pred_node_to_nodes[to_con]
    for _, fr_con in enumerate(candidate_fr_nodes):
      #condition1 = not (fr_node in subgraph[0])
      condition1 = not (fr_con in subgraph[0])
      condition2 = concrete_node_belong_node_var(GDL_program.nodeVars[node_var_fr], fr_con, my_maps.X_node)
      if condition1 and condition2:

        new_subgraph = copy.deepcopy(subgraph)
        new_subgraph[0].append(fr_con)
        new_subgraph[1].append((fr_con, to_con))
        if exist_subgraph_NC_DFS(new_subgraph, new_sub_GDL_program, GDL_program, my_maps, edge_var_idx + 1) == 0:
          return 0

  elif case == 0:
    node_var_fr = target_edge_var[1]
    node_var_to = target_edge_var[2]
    fr_con = subgraph[0][node_var_fr]

    candidate_to_nodes = my_maps.succ_node_to_nodes[fr_con]
    for _, to_con  in enumerate(candidate_to_nodes):
      condition1 = not (to_con in subgraph[0])
      condition2 = concrete_node_belong_node_var(GDL_program.nodeVars[node_var_to], to_con, my_maps.X_node)
      if condition1 and condition2:
        new_subgraph = copy.deepcopy(subgraph)
        new_subgraph[0].append(to_con)
        new_subgraph[1].append((fr_con, to_con))
        if exist_subgraph_NC_DFS(new_subgraph, new_sub_GDL_program, GDL_program, my_maps, edge_var_idx + 1) == 0:
          return 0
  else:
    raise Undefined()
  return 1


#node_projection
def find_matching_subgraph_NC(GDL_program, my_maps, predicted_node):
  
  subgraphs = [] 
  node_var_idx_to_concrete_nodes = {}

  for idx, node_var in enumerate(GDL_program.nodeVars):
    node_var_idx_to_concrete_nodes[idx] = eval_node_var(node_var, my_maps.nodes, my_maps.X_node)

  sub_GDL_program = [[0],[]]

  for _, concrete_node in enumerate(node_var_idx_to_concrete_nodes[0]):
    subgraphs.append(([concrete_node],[]))
  
  #print(len(subgraphs))
  
  candidate_edge_vars = copy.deepcopy(GDL_program.edgeVars) 
  while(len(candidate_edge_vars) > 0):
    (edge_var, sub_GDL_program_edge, sub_GDL_program, case) = choose_an_edge_var_and_update_sub_GDL_program_NC(sub_GDL_program, candidate_edge_vars)
    del candidate_edge_vars[0]
    subgraphs = update_subgraphs_NC(edge_var, sub_GDL_program_edge, subgraphs, sub_GDL_program, case, node_var_idx_to_concrete_nodes, my_maps)
    #print(len(subgraphs))
  chosen_nodes = set()
  for _, [nodes,edges] in enumerate(subgraphs):
    if nodes[0] == predicted_node:
      return [nodes, edges]

  #print("Cannot be happened") 
  raise Undefined()


#node_projection
def eval_GDL_program_NC(GDL_program, my_maps):
  
  subgraphs = [] 
  node_var_idx_to_concrete_nodes = {}

  for idx, node_var in enumerate(GDL_program.nodeVars):
    node_var_idx_to_concrete_nodes[idx] = eval_node_var(node_var, my_maps.nodes, my_maps.X_node)

  sub_GDL_program = [[0],[]]

  for _, concrete_node in enumerate(node_var_idx_to_concrete_nodes[0]):
    subgraphs.append(([concrete_node],[]))

  print(len(subgraphs))


  candidate_edge_vars = copy.deepcopy(GDL_program.edgeVars) 
  while(len(candidate_edge_vars) > 0):
    (edge_var, sub_GDL_program_edge, sub_GDL_program, case) = choose_an_edge_var_and_update_sub_GDL_program_NC(sub_GDL_program, candidate_edge_vars)
    del candidate_edge_vars[0]
    subgraphs = update_subgraphs_NC(edge_var, sub_GDL_program_edge, subgraphs, sub_GDL_program, case, node_var_idx_to_concrete_nodes, my_maps)
    #print(len(subgraphs))
  
  chosen_nodes = set()
  for _, [nodes,edges] in enumerate(subgraphs):
    chosen_nodes.add(nodes[0])
  return chosen_nodes 



def choose_an_edge_var_and_update_sub_GDL_program_NC(sub_GDL_program, candidate_edge_vars):
  (_, p, q) = candidate_edge_vars[0]
  idx = len(sub_GDL_program[1]) 
  if (p in sub_GDL_program[0]) and (q in sub_GDL_program[0]):
    sub_GDL_program[1].append((p, q))
    case = 2
    
  elif (q in sub_GDL_program[0]): 
    sub_GDL_program[0].append(p)
    sub_GDL_program[1].append((p, q))
    case = 1 
  elif (p in sub_GDL_program[0]): 
    sub_GDL_program[0].append(q)
    sub_GDL_program[1].append((p, q))
    case = 0
  
  else:
    raise("This cannot be happened")
  
  return ((p, q, idx), (sub_GDL_program[0].index(p), sub_GDL_program[0].index(q)), sub_GDL_program, case)      


def update_subgraphs_NC(edge_var, sub_graph_node_indices, subgraphs, sub_GDL_program, case, node_var_idx_to_concrete_nodes, my_maps):
  (p_abs, q_abs, edge_var_idx) = edge_var
  (p_sub, q_sub) = sub_graph_node_indices

  new_subgraphs = []
  for _, [nodes, edges] in enumerate(subgraphs):

    #addsucc
    if case == 0 :
      p_con = nodes[p_sub]
      candidate_q_cons = my_maps.succ_node_to_nodes[p_con]
      for _, q_con in enumerate(candidate_q_cons):
        if (q_con in node_var_idx_to_concrete_nodes[q_abs]) and not (q_con in nodes):
          my_new_subgraph = copy.deepcopy([nodes,edges])
          my_new_subgraph[1].append((p_con, q_con))
          my_new_subgraph[0].append(q_con)
          new_subgraphs.append(my_new_subgraph)
          
    #addpred
    elif case == 1 :
      q_con = nodes[q_sub]
      candidate_p_cons = my_maps.pred_node_to_nodes[q_con]
      for _, p_con in enumerate(candidate_p_cons):
        if (p_con in node_var_idx_to_concrete_nodes[p_abs]) and not (p_con in nodes):
          my_new_subgraph = copy.deepcopy([nodes,edges])
          my_new_subgraph[1].append((p_con, q_con))
          my_new_subgraph[0].append(p_con)
          new_subgraphs.append(my_new_subgraph)

    #addloop
    elif case == 2:
      p_con = nodes[p_sub]
      q_con == nodes[q_sub]
      my_new_subgraph = copy.deepcopy([nodes,edges])
      my_new_subgraph[1].append((p_con, q_con))
      new_subgraphs.append(my_new_subgraph)

    else:
      raise ("This cannot be happened") 
    
  return new_subgraphs


def concrete_node_belong_node_var(node_var, node, X_node):
  for _, feat_idx in enumerate(node_var):
    (bot, top) = node_var[feat_idx]
    if X_node[node][feat_idx] < bot or top < X_node[node][feat_idx]:
      return False
  return True 


def concrete_edge_belong_edge_var(edge_var, edge, X_edge):
  #print(edge_var)
  (itvs, p, q) = edge_var 
  for _, feat_idx in enumerate(itvs):
    (bot, top) = itvs[feat_idx]
    if X_edge[edge][feat_idx] < bot or top < X_edge[edge][feat_idx]:
      return False
  return True 


def get_edge_var_case_and_update_sub_GDL_program(sub_GDL_program, edge_var):
  (_, p, q) = edge_var
  sub_node_vars = sub_GDL_program[0]
  if (p in sub_node_vars) and (q in sub_node_vars):
    sub_GDL_program[1].append((p, q))
    case = 2
  elif (q in sub_node_vars): 
    sub_GDL_program[0].append(p)
    sub_GDL_program[1].append((p, q))
    case = 1 
  elif (p in sub_node_vars): 
    sub_GDL_program[0].append(q)
    sub_GDL_program[1].append((p, q))
    case = 0
  else:
    print("p : {}".format(p))
    print("q : {}".format(q))
    print("sub_node_vars : {}".format(sub_node_vars))
    print("sub_node_vars : {}".format(sub_GDL_program[1]))

    raise("Cannot be happened")
  return (sub_GDL_program, case)


def print_GDL_program(GDL_program, representation_type):
  
  if representation_type == 'nameless':
    #Nameless representation
    print("---------------- GDL program (Nameless representation) ----------------")
    print("nodeVars (first one is the target)")
    print(GDL_program.nodeVars)
    print("edgeVars")
    print(GDL_program.edgeVars)

  elif representation_type == 'normal':
    print("-------------- GDL program  --------------")
    nodeVars = GDL_program.nodeVars
    for idx in range(len(nodeVars)):
      if len(nodeVars[idx]) == 0:
        print("node v{}".format(idx))
      else:
        print("node v{} {}".format(idx, nodeVars[idx]))
    edgeVars = GDL_program.edgeVars
    for idx in range(len(edgeVars)):
      if len(edgeVars[idx][0]) == 0:
        print("edge (v{}, v{})".format(edgeVars[idx][1], edgeVars[idx][2]))
      else:
        print("edge (v{}, v{}) {}".format(edgeVars[idx][1], edgeVars[idx][2], edgeVars[idx][0]))
    print("target node v1")
    print("------------------------------------------")



