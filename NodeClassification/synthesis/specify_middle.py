from language import *
from synthesis.score import score
import copy
import json
import sys


def specify_middle(GDL_program, data):
  best_score = score(GDL_program, data)
  best_GDL_program = GDL_program

  print ("Current Best GDL program")
  print (best_GDL_program.nodeVars)
  print (best_GDL_program.edgeVars)
  print ("Curret Best score : " + str(best_score))
  candidate_GDL_programs = set([GDL_program]) 
  for depth in range(data.chosen_depth):
    print()
    print("=====================================")
    print("Depth : {}".format(depth))
    print("=====================================")
    print()

    new_candidate_GDL_programs = set()
    for _, GDL_program in enumerate(candidate_GDL_programs): 
    
      for i in range(len(GDL_program.nodeVars)):
        for j in range(len(data.X_node[0])):
          feature_list = data.feature_list[j]
          feature_list_rev = data.feature_list_rev[j]
          min_max_feature = data.min_max_feature[j]

          node_var = GDL_program.nodeVars[i]
          if j in node_var:
            bot = node_var[j][0]
            top = node_var[j][1]
            top_idx = feature_list.index(top)

            bot_idx = feature_list_rev.index(bot)
            bot_idx = len(feature_list) - bot_idx
            new_GDL_program = copy.deepcopy(GDL_program)

            if feature_list[top_idx -1] == bot :
              new_GDL_program.nodeVars[i][j] = (bot, bot)

            else:
              new_GDL_program.nodeVars[i][j] = (bot, feature_list[int((top_idx+bot_idx)/2)])
            new_score = score(new_GDL_program, data)
            if depth < data.chosen_depth-1:
              new_candidate_GDL_programs.add(new_GDL_program)
            if (new_score > best_score):
              best_score = new_score
              best_GDL_program = new_GDL_program
              print ("Current Best GDL_program")
              print_GDL_program(new_GDL_program,'nameless')
              #print (new_GDL_program.nodeVars)
              #print (new_GDL_program.edgeVars)
              print ("Current Best score : " + str(best_score))
            

            new_GDL_program = copy.deepcopy(GDL_program)
            
            if feature_list[top_idx -1] == bot :
              new_GDL_program.nodeVars[i][j] = (top, top)
            else:
              new_GDL_program.nodeVars[i][j] = (feature_list[int((top_idx+bot_idx)/2)], top)
            new_score = score(new_GDL_program, data)
            if depth < data.chosen_depth-1:
              new_candidate_GDL_programs.add(new_GDL_program)
            if (new_score > best_score):
              best_score = new_score
              best_GDL_program = new_GDL_program
              print ("Current Best GDL_program")
              print_GDL_program(new_GDL_program,'nameless')
              #print (new_GDL_program.nodeVars)
              #print (new_GDL_program.edgeVars)
              print ("Current Best score : " + str(best_score))
            

          #ToDo 
          else:    
            top = min_max_feature[0][1] 
            bot = feature_list[int(len(feature_list)/2)] 
            new_GDL_program = copy.deepcopy(GDL_program)
            new_GDL_program.nodeVars[i][j] = (bot, top)
            new_score = score(new_GDL_program, data)
            if depth < data.chosen_depth-1:
              new_candidate_GDL_programs.add(new_GDL_program)
            '''if (new_score >= best_score):'''
            if (new_score > best_score):
              best_score = new_score
              best_GDL_program = new_GDL_program
              print ("Current Best GDL_program")
              print_GDL_program(new_GDL_program,'nameless')
              #print (new_GDL_program.nodeVars)
              #print (new_GDL_program.edgeVars)
              print ("Current Best score : " + str(best_score))


            bot = min_max_feature[0][0] 
            top = feature_list[int(len(feature_list)/2)] 
            new_GDL_program = copy.deepcopy(GDL_program)
            new_GDL_program.nodeVars[i][j] = (bot, top)
            new_score = score(new_GDL_program, data)
            if depth < data.chosen_depth-1:
              new_candidate_GDL_programs.add(new_GDL_program)
            '''if (new_score >= best_score):'''
            if (new_score > best_score):
              best_score = new_score
              best_GDL_program = new_GDL_program
              print ("Current Best GDL_program")
              print_GDL_program(new_GDL_program,'nameless')
              #print (new_GDL_program.nodeVars)
              #print (new_GDL_program.edgeVars)
              print ("Current Best score : " + str(best_score))
      if len(GDL_program.nodeVars) < 3:
        for j in range(len(data.X_node[0])):
          new_node = {}
          bot = feature_list[int(len(feature_list)/2)] 
          top = min_max_feature[0][1] 
          #top = 1
          new_node[j] = (bot,top)
          q = len(GDL_program.nodeVars)
          for p in range(len(GDL_program.nodeVars)):
            new_GDL_program = copy.deepcopy(GDL_program)
            new_GDL_program.nodeVars.append(new_node)
            new_GDL_program.edgeVars.append( ({}, q, p) )

            new_score = score(new_GDL_program, data)
            if depth < data.chosen_depth-1:
              new_candidate_GDL_programs.add(new_GDL_program)
            '''if (new_score >= best_score):'''
            if (new_score > best_score):
              best_score = new_score
              best_GDL_program = new_GDL_program
              print ("Current Best GDL_program")
              print_GDL_program(new_GDL_program,'nameless')
              #print (new_GDL_program.nodeVars)
              #print (new_GDL_program.edgeVars)
              print ("Current Best score : " + str(best_score))

          new_node = {}
          #bot = 0.0 
          bot = min_max_feature[0][0] 
          top = feature_list[int(len(feature_list)/2)] 
          new_node[j] = (bot, top)

          new_node[j] = (bot,top)
          q = len(GDL_program.nodeVars)

          for p in range(len(GDL_program.nodeVars)):
            new_GDL_program = copy.deepcopy(GDL_program)
            new_GDL_program.nodeVars.append(new_node)
            new_GDL_program.edgeVars.append( ({}, q, p) )

            new_score = score(new_GDL_program, data)
            if depth < data.chosen_depth - 1:
              new_candidate_GDL_programs.add(new_GDL_program)
            '''if (new_score >= best_score):'''
            if (new_score > best_score):
              best_score = new_score
              best_GDL_program = new_GDL_program
              print ("Current Best GDL_program")
              print_GDL_program(new_GDL_program,'nameless')
              #print (new_GDL_program.nodeVars)
              #print (new_GDL_program.edgeVars)
              print ("Current Best score : " + str(best_score))

        if data.is_undirected:
          continue

        for j in range(len(data.X_node[0])):
          new_node = {}
          bot = feature_list[int(len(feature_list)/2)] 
          top = min_max_feature[0][1] 
          #top = 1
          new_node[j] = (bot,top)
          q = len(GDL_program.nodeVars)
          for p in range(len(GDL_program.nodeVars)):
            new_GDL_program = copy.deepcopy(GDL_program)
            new_GDL_program.nodeVars.append(new_node)
            new_GDL_program.edgeVars.append( ({}, p, q) )

            new_score = score(new_GDL_program, data)
            if depth < data.chosen_depth-1:
              new_candidate_GDL_programs.add(new_GDL_program)
            '''if (new_score >= best_score):'''
            if (new_score > best_score):
              best_score = new_score
              best_GDL_program = new_GDL_program
              print ("Current Best GDL_program")
              print_GDL_program(new_GDL_program,'nameless')
              #print (new_GDL_program.nodeVars)
              #print (new_GDL_program.edgeVars)
              print ("Current Best score : " + str(best_score))

          new_node = {}
          #bot = 0.0 
          bot = min_max_feature[0][0] 
          top = feature_list[int(len(feature_list)/2)] 
          new_node[j] = (bot, top)

          new_node[j] = (bot,top)
          q = len(GDL_program.nodeVars)

          for p in range(len(GDL_program.nodeVars)):
            new_GDL_program = copy.deepcopy(GDL_program)
            new_GDL_program.nodeVars.append(new_node)
            new_GDL_program.edgeVars.append( ({}, p, q) )

            new_score = score(new_GDL_program, data)
            if depth < data.chosen_depth-1:
              new_candidate_GDL_programs.add(new_GDL_program)
            '''if (new_score >= best_score):'''
            if (new_score > best_score):
              best_score = new_score
              best_GDL_program = new_GDL_program
              print ("Current Best GDL_program")
              print_GDL_program(new_GDL_program,'nameless')
              #print (new_GDL_program.nodeVars)
              #print (new_GDL_program.edgeVars)
              print ("Current Best score : " + str(best_score))

    candidate_GDL_programs = new_candidate_GDL_programs
  print ("Best GDL program")
  print_GDL_program(best_GDL_program,'nameless')
  #print (best_GDL_program.nodeVars)
  #print (best_GDL_program.edgeVars)
  return (best_GDL_program, best_score) 





