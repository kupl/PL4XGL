from data_loader import *
from language import *
import copy
import json



def additional_learn_GDL_programs(data):
  data.GDL_program_dict = set()
  GDL_program = GDL()
  GDL_program.nodeVars = [{}]
  GDL_program.edgeVars = []
  my_GDL_programs = set()
  candidate_GDL_programs = set([GDL_program])
  my_depth = 1 
  for depth in range(my_depth): 
    print()
    print("=========================================")
    print("Depth : {}".format(depth))
    print("=========================================")
    print()
    print("Candidate abstract graph len : {}".format(len(candidate_GDL_programs)))
    new_candidate_GDL_programs = set()
    for _, GDL_program in enumerate(candidate_GDL_programs):
      for i in range(len(GDL_program.nodeVars)):
        print(GDL_program.nodeVars[i])
        if len(GDL_program.nodeVars[i]) > 0:
          continue
        for j in range(len(data.X_node[0])):
          abs_node = GDL_program.nodeVars[i]
          if not j in abs_node:
            bot = 0.5
            top = 1.0
            new_GDL_program = copy.deepcopy(GDL_program)
            new_GDL_program.nodeVars[i][j] = (bot, top)
            #key = json.dumps(new_sentence.absList)
            key = (json.dumps(new_GDL_program.nodeVars), json.dumps(new_GDL_program.edgeVars))
            if not key in data.GDL_program_dict:
              data.GDL_program_dict.add(key)
              new_score = my_score(new_GDL_program, data)
              if new_score > 0.5:
                #if new_score > data.default_score * data.expected:
                print()
                print("New AbsGraph")
                print(new_GDL_program.nodeVars)
                print(new_GDL_program.edgeVars)
                print("Score : {}".format(new_score))
                my_GDL_programs.add(new_GDL_program)
                new_candidate_GDL_programs.add(new_GDL_program)
      if len(GDL_program.nodeVars) < 3:
        for j in range(len(data.X_node[0])): 
          new_node = {}
          bot = 0.5
          top = 1.0
          new_node[j] = (bot,top)
          p = len(GDL_program.nodeVars)
          for q in range(len(GDL_program.nodeVars)):
            new_GDL_program = copy.deepcopy(GDL_program)
            new_GDL_program.nodeVars.append(new_node)
            new_GDL_program.edgeVars.append( ({}, p, q) )
            #key = json.dumps(new_sentence.absList)
            key = (json.dumps(new_GDL_program.nodeVars), json.dumps(new_GDL_program.edgeVars))
            if not key in data.GDL_program_dict:
              data.GDL_program_dict.add(key)
              new_score = my_score(new_GDL_program, data)
              if new_score > 0.4:
                #if new_score > data.expected:
                print()
                print("New AbsGraph")
                print(new_GDL_program.nodeVars)
                print(new_GDL_program.edgeVars)
                print("Score : {}".format(new_score))
                my_GDL_programs.add(new_GDL_program)
                new_candidate_GDL_programs.add(new_GDL_program)
        if data.is_undirected:
          continue
        for j in range(len(data.X_node[0])): 
          new_node = {}
          bot = 0.5
          top = 1.0
          new_node[j] = (bot, top)
          q = len(GDL_program.nodeVars)
          for p in range(len(GDL_program.nodeVars)):
            new_GDL_program = copy.deepcopy(GDL_program)
            new_GDL_program.nodeVars.append(new_node)
            new_GDL_program.edgeVars.append( ({}, p, q) )
            #key = json.dumps(new_sentence.absList)
            key = (json.dumps(new_GDL_program.nodeVars), json.dumps(new_GDL_program.edgeVars))
            if not key in data.GDL_program_dict:
              data.GDL_program_dict.add(key)
              new_score = my_score(new_GDL_program, data)
              if new_score > 0.5:
                #if new_score > data.default_score * data.expedted:
                print()
                print("New AbsGraph")
                print(new_GDL_program.nodeVars)
                print(new_GDL_program.edgeVars)
                print("Score : {}".format(new_score))
                my_GDL_programs.add(new_GDL_program)
                new_candidate_GDL_programs.add(new_GDL_program)
    candidate_GDL_programs = new_candidate_GDL_programs
    print("New candidate GDL_programs len : {}".format(len(new_candidate_GDL_programs)))
  print("My_GDL_programs len : {}".format(len(my_GDL_programs)))
  return my_GDL_programs
        
def my_score(GDL_program, data):
  key = (json.dumps(GDL_program.nodeVars), json.dumps(GDL_program.edgeVars))
  if key in data.dict:
    nodes = data.dict[key]
  else:
    nodes = eval_GDL_program_NC_DFS(GDL_program, data) & data.train_nodes 
    data.dict[key] = nodes
  nodes = nodes & data.train_nodes
  score = float(len(data.original_labeled_nodes & nodes)) / float(len(nodes) + 0.1)
  return score



