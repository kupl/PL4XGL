from language import *
from synthesis.score import score
import copy
import json
import sys

def specify_mean(GDL_program, data):
  best_score = score(GDL_program, data)
  best_GDL_program = GDL_program
  print ("Current best GDL program") 
  print (best_GDL_program.nodeVars)
  print (best_GDL_program.edgeVars)
  print ("Curret Best score : " + str(best_score))
  #my_GDL_programs = set()
  print ("GDL_program len : " + str(len(GDL_program.nodeVars)))
  print ("features len : " + str(len(data.X_node[0])))
  print (data.chosen_depth)
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
          node_var = GDL_program.nodeVars[i]
          if j in node_var:
            if data.is_one_hot:
              continue
            

            # Specifying interval
            specify_interval()
            bot = node_var[j][0]
            top = node_var[j][1]

            new_GDL_program = copy.deepcopy(GDL_program)
            new_GDL_program.nodeVars[i][j] = (bot, (bot+top)/2)

            new_score = score(new_GDL_program, data)
            if (new_score > best_score):
              best_score = new_score
              best_GDL_program = new_GDL_program
              print ("Current Best GDL_program")
              print_GDL_program(new_GDL_program,'nameless')
              #print (new_GDL_program.nodeVars)
              #print (new_GDL_program.edgeVars)
              print ("Current Best score : " + str(best_score))
 
            new_GDL_program = copy.deepcopy(GDL_program)
            new_GDL_program.nodeVars[i][j] = ((bot+top)/2, top)

            new_score = score(new_GDL_program, data)
            if (new_score > best_score):
              best_score = new_score
              best_GDL_program = new_GDL_program
              print ("Current Best GDL_program")
              print_GDL_program(new_GDL_program,'nameless')
              #print (new_GDL_program.nodeVars)
              #print (new_GDL_program.edgeVars)
              print ("Current Best score : " + str(best_score))
          
         
          else:
            bot = (data.min_max_feature[j][1] + data.min_max_feature[j][0])/2
            top = data.min_max_feature[j][1]
            new_GDL_program = copy.deepcopy(GDL_program)
            new_GDL_program.nodeVars[i][j] = (bot, top)
            new_score = score(new_GDL_program, data)
            if depth < data.chosen_depth-1:
              new_candidate_GDL_programs.add(new_GDL_program)
            if (new_score > best_score):
              best_score = new_score
              best_GDL_program = new_GDL_program
              print ("Current Best GDL_program")
              print (new_GDL_program.nodeVars)
              print (new_GDL_program.edgeVars)
              print ("Current Best score : " + str(best_score))
            bot = data.min_max_feature[j][0]
            top = (data.min_max_feature[j][1] + data.min_max_feature[j][0])/2
            new_GDL_program = copy.deepcopy(GDL_program)
            new_GDL_program.nodeVars[i][j] = (bot, top)
            new_score = score(new_GDL_program, data)
            if depth < data.chosen_depth-1:
              new_candidate_GDL_programs.add(new_GDL_program)
            if (new_score > best_score):
              best_score = new_score
              best_GDL_program = new_GDL_program
              print ("Current Best GDL_program")
              print (new_GDL_program.nodeVars)
              print (new_GDL_program.edgeVars)
              print ("Current Best score : " + str(best_score))


      #add a new node var
      if len(GDL_program.nodeVars) < 3:
        for j in range(len(data.X_node[0])):
          new_node = {}
          bot = (data.min_max_feature[j][1] + data.min_max_feature[j][0])/2
          top = data.min_max_feature[j][1]
          new_node[j] = (bot,top)
          q = len(GDL_program.nodeVars)
          for p in range(len(GDL_program.nodeVars)):
            new_GDL_program = copy.deepcopy(GDL_program)
            new_GDL_program.nodeVars.append(new_node)
            new_GDL_program.edgeVars.append( ({}, q, p) )
            new_score = score(new_GDL_program, data)
            if depth < data.chosen_depth-1:
              new_candidate_GDL_programs.add(new_GDL_program)
            if (new_score > best_score):
              best_score = new_score
              best_GDL_program = new_GDL_program
              print ("Current Best GDL_program")
              print (new_GDL_program.nodeVars)
              print (new_GDL_program.edgeVars)
              print ("Current Best score : " + str(best_score))

          new_node = {}
          bot = data.min_max_feature[j][0]
          top = (data.min_max_feature[j][1] + data.min_max_feature[j][0])/2
          new_node[j] = (bot,top)
          q = len(GDL_program.nodeVars)
          for p in range(len(GDL_program.nodeVars)):
            new_GDL_program = copy.deepcopy(GDL_program)
            new_GDL_program.nodeVars.append(new_node)
            new_GDL_program.edgeVars.append( ({}, q, p) )
            new_score = score(new_GDL_program, data)
            if depth < data.chosen_depth-1:
              new_candidate_GDL_programs.add(new_GDL_program)
            if (new_score > best_score):
              best_score = new_score
              best_GDL_program = new_GDL_program
              print ("Current Best GDL_program")
              print (new_GDL_program.nodeVars)
              print (new_GDL_program.edgeVars)
              print ("Current Best score : " + str(best_score))


        if data.is_undirected:
          continue

        for j in range(len(data.X_node[0])):
          new_node = {}
          bot = (data.min_max_feature[j][1] + data.min_max_feature[j][0])/2
          top = data.min_max_feature[j][1]
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
              print (new_GDL_program.nodeVars)
              print (new_GDL_program.edgeVars)
              print ("Current Best score : " + str(best_score))


          new_node = {}
          bot = data.min_max_feature[j][1]
          top = (data.min_max_feature[j][1] + data.min_max_feature[j][0])/2
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
              print (new_GDL_program.nodeVars)
              print (new_GDL_program.edgeVars)
              print ("Current Best score : " + str(best_score))


    candidate_GDL_programs = new_candidate_GDL_programs
  print ("The Best GDL program")
  print (best_GDL_program.nodeVars)
  print (best_GDL_program.edgeVars)
  return (best_GDL_program, best_score) 


