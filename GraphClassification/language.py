import copy

class GDL:
  # Nameless representation      
  def __init__(self):
    # constraint list for the node variables in the GDL program
    self.nodeVars = []
    # constraint list for the edge variables in the GDL program    
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

def eval_GDL_program_on_graphs_GC_test_graphs(GDL_program, data):
  chosen_graphs = set()
  for i, graph in enumerate(data.graphs):
    if i in data.test_graphs:
      if eval_GDL_program_DFS(GDL_program, graph, data):
        chosen_graphs.add(i)
  return chosen_graphs

def eval_GDL_program_on_graphs_GC(GDL_program, data):
  chosen_graphs = set()
  for i, graph in enumerate(data.graphs):
    if eval_GDL_program_DFS(GDL_program, graph, data):
      chosen_graphs.add(i)
  return chosen_graphs


def eval_GDL_program_on_graphs_GC_Score(GDL_program, data, labeled_graphs):
  correct_set = set()
  incorrect_set = set()
  edge_vars_len = len(GDL_program.edgeVars)

  for i, graph in enumerate(data.graphs):
    if not (i in data.train_graphs):
      continue
    edges_len = len(graph[1])
    if (edge_vars_len > edges_len):
      continue
    exists = eval_GDL_program_DFS(GDL_program, graph, data) #ToDo

    if exists:
      if (i in labeled_graphs):
        correct_set.add(i)
      else:
        incorrect_set.add(i)

  correct_graphs_len = len(correct_set)
  incorrect_graphs_len = len(incorrect_set)
  accuracy =  correct_graphs_len/(correct_graphs_len + incorrect_graphs_len + data.epsilon)
  score = accuracy
  return score 


def eval_GDL_program_on_graphs_GC_Score_graphs(GDL_program, data, labeled_graphs):
  correct_set = set()
  incorrect_set = set()
  edge_vars_len = len(GDL_program.edgeVars)

  for i, graph in enumerate(data.graphs):
    if not (i in data.train_graphs):
      continue
    edges_len = len(graph[1])
    if (edge_vars_len > edges_len):
      continue
    exists = eval_GDL_program_DFS(GDL_program, graph, data) #ToDo

    if exists:
      if (i in labeled_graphs):
        correct_set.add(i)
      else:
        incorrect_set.add(i)

  correct_graphs_len = len(correct_set)
  incorrect_graphs_len = len(incorrect_set)
  accuracy =  correct_graphs_len/(correct_graphs_len + incorrect_graphs_len + data.epsilon)
  score = accuracy
  chosen_graphs = correct_set | incorrect_set
  return score, chosen_graphs 



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


def eval_GDL_program_DFS(GDL_program, graph, data):   
  edges = graph[1]
  edge_var_first = GDL_program.edgeVars[0]
  node_var_fr = edge_var_first[1]
  node_var_to = edge_var_first[2]
  candidate_edges = set()
  for _, edge in enumerate(edges):
    condition1 = concrete_edge_belong_edge_var(edge_var_first, edge, data.X_edge)
    condition2 = concrete_node_belong_node_var(GDL_program.nodeVars[node_var_fr], data.A[edge][0], data.X_node)
    condition3 = concrete_node_belong_node_var(GDL_program.nodeVars[node_var_to], data.A[edge][1], data.X_node)
    if condition1 and condition2 and condition3:
      candidate_edges.add(edge) 

  for _, init_graph_edge in enumerate(candidate_edges):
    node_var_idx_to_concrete_node = {}
    edge_var_idx_to_concrete_edge = {}

    sub_GDL_program_edge = (node_var_fr, node_var_to)
    sub_GDL_program = [[node_var_fr, node_var_to],[sub_GDL_program_edge]]
    subgraph = [[],[]]
    subgraph[0].append(data.A[init_graph_edge][0])
    subgraph[0].append(data.A[init_graph_edge][1])
    subgraph[1].append(init_graph_edge)
    node_var_idx_to_concrete_node[node_var_fr] = data.A[init_graph_edge][0]
    node_var_idx_to_concrete_node[node_var_to] = data.A[init_graph_edge][1]
    edge_var_idx_to_concrete_edge[0] = init_graph_edge
    
    if exist_subgraph_DFS(subgraph, sub_GDL_program, GDL_program, graph, 1, node_var_idx_to_concrete_node, edge_var_idx_to_concrete_edge, data) == 0:
      return True
  return False


def exist_subgraph_DFS(subgraph, sub_GDL_program, GDL_program, graph, edge_var_idx, node_var_idx_to_concrete_node, edge_var_idx_to_concrete_edge, my_maps):
  #print(subgraph)
  if len(GDL_program.edgeVars) == edge_var_idx:
    return 0 
  target_edge_var = GDL_program.edgeVars[edge_var_idx]
  new_sub_GDL_program = copy.deepcopy(sub_GDL_program)
  (new_sub_GDL_program, case) = get_edge_var_case_and_update_sub_GDL_program(new_sub_GDL_program, target_edge_var)
  if case == 2:
    node_var_fr = target_edge_var[1]
    node_var_to = target_edge_var[2]
    fr_con = node_var_idx_to_concrete_node[node_var_fr]
    to_con = node_var_idx_to_concrete_node[node_var_to]
    if (fr_con, to_con) in my_maps.nodes_to_edge:
      con_edge = my_maps.nodes_to_edge[(fr_con, to_con)]
      #print(con_edge)
      if concrete_edge_belong_edge_var(target_edge_var, con_edge, my_maps.X_edge):
        new_edge_var_idx_to_concrete_edge = copy.deepcopy(edge_var_idx_to_concrete_edge)
        new_edge_var_idx_to_concrete_edge[edge_var_idx] = con_edge 
        new_subgraph = copy.deepcopy(subgraph)
        new_subgraph[1].append(con_edge)
        if exist_subgraph_DFS(new_subgraph, new_sub_GDL_program, GDL_program, graph, edge_var_idx + 1, node_var_idx_to_concrete_node, new_edge_var_idx_to_concrete_edge, my_maps) == 0:
          return 0
  elif case == 1: 
    #new_fr
    node_var_fr = target_edge_var[1] # checkthis
    node_var_to = target_edge_var[2]
    to_con = node_var_idx_to_concrete_node[node_var_to]
    candidate_fr_nodes = my_maps.pred_node_to_nodes[to_con]
    for _, (con_edge, fr_con) in enumerate(candidate_fr_nodes):
      #condition1 = not (fr_node in subgraph[0])
      condition1 = not (fr_con in subgraph[0])
      condition2 = concrete_node_belong_node_var(GDL_program.nodeVars[node_var_fr], my_maps.A[con_edge][0], my_maps.X_node)
      condition3 = concrete_edge_belong_edge_var(target_edge_var, con_edge, my_maps.X_edge)
      if condition1 and condition2 and condition3:
        new_node_var_idx_to_concrete_node = copy.deepcopy(node_var_idx_to_concrete_node)
        new_edge_var_idx_to_concrete_edge = copy.deepcopy(edge_var_idx_to_concrete_edge)
        new_edge_var_idx_to_concrete_edge[edge_var_idx] = con_edge
        new_node_var_idx_to_concrete_node[target_edge_var[1]] = fr_con

        new_subgraph = copy.deepcopy(subgraph)
        new_subgraph[0].append(fr_con)
        new_subgraph[1].append(con_edge)
        if exist_subgraph_DFS(new_subgraph, new_sub_GDL_program, GDL_program, graph, edge_var_idx + 1, new_node_var_idx_to_concrete_node, new_edge_var_idx_to_concrete_edge, my_maps) == 0:
          return 0
  elif case == 0:
    #new_to
    node_var_fr = target_edge_var[1]
    node_var_to = target_edge_var[2]
    fr_con = node_var_idx_to_concrete_node[node_var_fr]
    #print(my_maps.succ_node_to_nodes)
    candidate_to_nodes = my_maps.succ_node_to_nodes[fr_con]
    for _, val  in enumerate(candidate_to_nodes):
      (con_edge, to_con) = val
      condition1 = not (to_con in subgraph[0])
      condition2 = concrete_node_belong_node_var(GDL_program.nodeVars[node_var_to], my_maps.A[con_edge][1], my_maps.X_node)
      condition3 = concrete_edge_belong_edge_var(target_edge_var, con_edge, my_maps.X_edge)
      if condition1 and condition2 and condition3:
        new_node_var_idx_to_concrete_node = copy.deepcopy(node_var_idx_to_concrete_node)
        new_node_var_idx_to_concrete_node[target_edge_var[2]] = to_con
        new_edge_var_idx_to_concrete_edge = copy.deepcopy(edge_var_idx_to_concrete_edge)
        new_edge_var_idx_to_concrete_edge[edge_var_idx] = con_edge

        new_subgraph = copy.deepcopy(subgraph)
        new_subgraph[0].append(to_con)
        new_subgraph[1].append(con_edge)
        if exist_subgraph_DFS(new_subgraph, new_sub_GDL_program, GDL_program, graph, edge_var_idx + 1, new_node_var_idx_to_concrete_node, new_edge_var_idx_to_concrete_edge, my_maps) == 0:
          return 0
  else:
    raise("Cannot be happened")
  return 1


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

    raise("Something wrong!")
  return (sub_GDL_program, case)


def find_matching_subgraph(GDL_program, graph, data):   
  edges = graph[1]
  edge_var_first = GDL_program.edgeVars[0]
  node_var_fr = edge_var_first[1]
  node_var_to = edge_var_first[2]
  candidate_edges = set()
  for _, edge in enumerate(edges):
    condition1 = concrete_edge_belong_edge_var(edge_var_first, edge, data.X_edge)
    condition2 = concrete_node_belong_node_var(GDL_program.nodeVars[node_var_fr], data.A[edge][0], data.X_node)
    condition3 = concrete_node_belong_node_var(GDL_program.nodeVars[node_var_to], data.A[edge][1], data.X_node)
    if condition1 and condition2 and condition3:
      candidate_edges.add(edge) 

  for _, init_graph_edge in enumerate(candidate_edges):
    node_var_idx_to_concrete_node = {}
    edge_var_idx_to_concrete_edge = {}

    sub_GDL_program_edge = (node_var_fr, node_var_to)
    sub_GDL_program = [[node_var_fr, node_var_to],[sub_GDL_program_edge]]
    subgraph = [[],[]]
    subgraph[0].append(data.A[init_graph_edge][0])
    subgraph[0].append(data.A[init_graph_edge][1])
    subgraph[1].append(init_graph_edge)
    node_var_idx_to_concrete_node[node_var_fr] = data.A[init_graph_edge][0]
    node_var_idx_to_concrete_node[node_var_to] = data.A[init_graph_edge][1]
    edge_var_idx_to_concrete_edge[0] = init_graph_edge
    val = find_subgraph_DFS(subgraph, sub_GDL_program, GDL_program, graph, 1, node_var_idx_to_concrete_node, edge_var_idx_to_concrete_edge, data)
    if val[0] == 0:
      return val[1]  
  return None

def find_subgraph_DFS(subgraph, sub_GDL_program, GDL_program, graph, edge_var_idx, node_var_idx_to_concrete_node, edge_var_idx_to_concrete_edge, my_maps):
  #print(subgraph)
  if len(GDL_program.edgeVars) == edge_var_idx:
    return (0, subgraph)

  target_edge_var = GDL_program.edgeVars[edge_var_idx]
  new_sub_GDL_program = copy.deepcopy(sub_GDL_program)
  (new_sub_GDL_program, case) = get_edge_var_case_and_update_sub_GDL_program(new_sub_GDL_program, target_edge_var)
  if case == 2:
    node_var_fr = target_edge_var[1]
    node_var_to = target_edge_var[2]
    fr_con = node_var_idx_to_concrete_node[node_var_fr]
    to_con = node_var_idx_to_concrete_node[node_var_to]
    if (fr_con, to_con) in my_maps.nodes_to_edge:
      con_edge = my_maps.nodes_to_edge[(fr_con, to_con)]
      #print(con_edge)
      if concrete_edge_belong_edge_var(target_edge_var, con_edge, my_maps.X_edge):
        new_edge_var_idx_to_concrete_edge = copy.deepcopy(edge_var_idx_to_concrete_edge)
        new_edge_var_idx_to_concrete_edge[edge_var_idx] = con_edge 
        new_subgraph = copy.deepcopy(subgraph)
        new_subgraph[1].append(con_edge)
        val = find_subgraph_DFS(new_subgraph, new_sub_GDL_program, GDL_program, graph, edge_var_idx + 1, node_var_idx_to_concrete_node, new_edge_var_idx_to_concrete_edge, my_maps)
        print(val)
        if val[0] == 0:
          return val
  elif case == 1: 
    #new_fr
    node_var_fr = target_edge_var[1] # checkthis
    node_var_to = target_edge_var[2]
    to_con = node_var_idx_to_concrete_node[node_var_to]
    candidate_fr_nodes = my_maps.pred_node_to_nodes[to_con]
    for _, (con_edge, fr_con) in enumerate(candidate_fr_nodes):
      #condition1 = not (fr_node in subgraph[0])
      condition1 = not (fr_con in subgraph[0])
      condition2 = concrete_node_belong_node_var(GDL_program.nodeVars[node_var_fr], my_maps.A[con_edge][0], my_maps.X_node)
      condition3 = concrete_edge_belong_edge_var(target_edge_var, con_edge, my_maps.X_edge)
      if condition1 and condition2 and condition3:
        new_node_var_idx_to_concrete_node = copy.deepcopy(node_var_idx_to_concrete_node)
        new_edge_var_idx_to_concrete_edge = copy.deepcopy(edge_var_idx_to_concrete_edge)
        new_edge_var_idx_to_concrete_edge[edge_var_idx] = con_edge
        new_node_var_idx_to_concrete_node[target_edge_var[1]] = fr_con

        new_subgraph = copy.deepcopy(subgraph)
        new_subgraph[0].append(fr_con)
        new_subgraph[1].append(con_edge)
        val = find_subgraph_DFS(new_subgraph, new_sub_GDL_program, GDL_program, graph, edge_var_idx + 1, new_node_var_idx_to_concrete_node, new_edge_var_idx_to_concrete_edge, my_maps)
        if val[0] == 0:
          return val        
  elif case == 0:
    #new_to
    node_var_fr = target_edge_var[1]
    node_var_to = target_edge_var[2]
    fr_con = node_var_idx_to_concrete_node[node_var_fr]
    #print(my_maps.succ_node_to_nodes)
    candidate_to_nodes = my_maps.succ_node_to_nodes[fr_con]
    for _, val  in enumerate(candidate_to_nodes):
      (con_edge, to_con) = val
      condition1 = not (to_con in subgraph[0])
      condition2 = concrete_node_belong_node_var(GDL_program.nodeVars[node_var_to], my_maps.A[con_edge][1], my_maps.X_node)
      condition3 = concrete_edge_belong_edge_var(target_edge_var, con_edge, my_maps.X_edge)
      if condition1 and condition2 and condition3:
        new_node_var_idx_to_concrete_node = copy.deepcopy(node_var_idx_to_concrete_node)
        new_node_var_idx_to_concrete_node[target_edge_var[2]] = to_con
        new_edge_var_idx_to_concrete_edge = copy.deepcopy(edge_var_idx_to_concrete_edge)
        new_edge_var_idx_to_concrete_edge[edge_var_idx] = con_edge

        new_subgraph = copy.deepcopy(subgraph)
        new_subgraph[0].append(to_con)
        new_subgraph[1].append(con_edge)
        val = find_subgraph_DFS(new_subgraph, new_sub_GDL_program, GDL_program, graph, edge_var_idx + 1, new_node_var_idx_to_concrete_node, new_edge_var_idx_to_concrete_edge, my_maps)
        if val[0] == 0:
          return val      
  else:
    raise("Cannot be happened")
  return (1, None)


def eval_single_node_GDL_program_on_graphs(node_var, data):
  chosen_graphs = set()
  for i, graph in enumerate(data.graphs):
    nodes = graph[0]
    matching_nodes = eval_node_var(node_var, nodes, data.X_node)
    if len(matching_nodes) > 0:
      chosen_graphs.add(i)
  return chosen_graphs


def remove_unreachable_nodes(GDL_program):
  current_edge_vars = copy.deepcopy(GDL_program.edgeVars)
  unreachable_node_indices = set()
  reachable_node_indices = set()
  for i in range(len(GDL_program.nodeVars)):
    unreachable_node_indices.add(i)
  for _, (_, fr, to) in enumerate(current_edge_vars):
    reachable_node_indices.add(fr)
    reachable_node_indices.add(to)
  reachable_node_indices = list(reachable_node_indices)
  reachable_node_indices.sort()
  filtered_node_vars = []
  for _, idx in enumerate(reachable_node_indices):
    filtered_node_vars.append(GDL_program.nodeVars[idx])
  unreachable_node_indices = list(unreachable_node_indices - set(reachable_node_indices))
  unreachable_node_indices.sort(reverse = True)
  #print()
  #print("Unreachable nodes : {}".format(unreachable_node_indices))
  #print("Reachable nodes : {}".format(reachable_node_indices))
  #print()
  updated_edge_vars = []
  for i, val in enumerate(current_edge_vars):
    (itv, fr, to) = val
    for _, unreachable_node in enumerate(unreachable_node_indices):
      #print(unreachable_node)
      if unreachable_node < fr:
        fr = fr - 1
      if unreachable_node < to:
        to = to - 1
      #GDL_program.edgeVars[i] = (itv, fr, to)
    #print((fr, to))
    updated_edge_vars.append((itv, fr, to))
    #current_edge_vars = copy.deepcopy(GDL_program.edgeVars)
  GDL_program.nodeVars = filtered_node_vars
  GDL_program.edgeVars = updated_edge_vars
  return GDL_program


def print_GDL_program(GDL_program, representation_type):
  if representation_type == 'nameless':
    # Nameless representation
    print("----------------  Nameless representation  ----------------")
    print("NodeVarConstraints")
    print(GDL_program.nodeVars)
    print("EdgeVarConstraints")  
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
    print("target graph")
    print("------------------------------------------")
  else:
    raise Exception("Not Implemented")
    
