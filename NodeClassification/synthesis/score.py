from language import *
import json

def score(GDL_program, data):
  key = (json.dumps(GDL_program.nodeVars), json.dumps(GDL_program.edgeVars))
  if key in data.dict:
    nodes = data.dict[key]
  else:  
    nodes = eval_GDL_program_NC_DFS(GDL_program, data) & data.train_nodes 
    data.dict[key] = nodes
  score = float(len(data.original_labeled_nodes & nodes)) / float(len(nodes) + data.epsilon)
  if len(data.left_nodes & nodes) == 0:  
    return 0.001
  else:
    return score


