from language import *
import copy
import json
import sys


def learn_GDL_programs_td_node_classification(data): 
  print("Chosen_depth : {}".format(data.chosen_depth))
  i = 1 
  GDL_programs = set()
  
  data.covered_nodes = set()
  print("labeled nodes : "+str(len(data.original_labeled_nodes)))
  print("COVERED nodes : "+str(len(data.covered_nodes)))
  print("ORIGINAL_LABELED_NODES nodes : "+str(len(data.original_labeled_nodes)))
  while(len(data.left_nodes)>0):
    print()
    print()
    print("Outer iteration : "+str(i))
    print ("")
    print ("--------------------------------------------")
    '''new_sentence = learn_a_sentence(node_to_nodes, X_arr, labeled_nodes, parameter.feature_results)'''
    new_GDL_program = GDL()
    new_GDL_program.nodeVars = [{}]
    new_GDL_program.edgeVars = []
    data.default_score = score(new_GDL_program, data)
    print("Default score : {}".format(data.default_score))
    (new_GDL_programs, new_GDL_program) = learn_a_GDL_program(data)
    chosen_nodes = eval_GDL_program_NC_DFS(new_GDL_program, data) 
    print ("# of chosen Nodes : "+str(len((chosen_nodes & data.train_nodes))))
    print ("Chosen Labeled Nodes : "+str(chosen_nodes & data.original_labeled_nodes & data.train_nodes))
    data.covered_nodes = data.covered_nodes | (data.original_labeled_nodes & chosen_nodes)
    print ("COVERED nodes : "+str(len(data.covered_nodes)))
    print ("============================================")
    
    GDL_programs = GDL_programs | new_GDL_programs
    data.left_nodes = data.left_nodes - chosen_nodes 
    print("left nodes : "+str(len(data.left_nodes)))
    i = i+1
  return GDL_programs



def learn_a_GDL_program(data):
  GDL_program = GDL()
  GDL_program.nodeVars = [{}]
  GDL_program.edgeVars = []
  
  current_score = -1.0
  new_score = 0.0
  current_GDL_program = GDL_program
  new_GDL_program = GDL_program 
  new_GDL_programs = set()
  i = 1
  data.filtered_nodes = data.train_nodes
  chosen_nodes = data.filtered_nodes
  while(new_score > current_score):
    current_GDL_program = new_GDL_program
    current_score = new_score
    print("")
    print("")
    print("---------------------------------------------------------------------")
    print("Inner iteration : "+str(i))
    if data.is_one_hot == True:
      (new_GDL_program, new_score) = specify_binary(current_GDL_program, data)
    else:
      (new_GDL_program, new_score) = specify(current_GDL_program, data)
    
    #Modified
    if new_score >= data.default_score * data.expected:
      new_GDL_programs.add(new_GDL_program) 
    #new_sentences = new_sentences | my_sentences
    print("new_GDL_program")
    print(new_GDL_program.nodeVars)
    print(new_GDL_program.edgeVars)
    chosen_nodes = eval_GDL_program_NC_DFS(new_GDL_program, data) 
    data.filtered_nodes = chosen_nodes & data.train_nodes
    print("# of chosen Nodes : "+str(len(chosen_nodes)))
    print("Chosen Labeled Nodes : "+str(chosen_nodes & data.original_labeled_nodes))
    if len(chosen_nodes) == len(chosen_nodes & data.original_labeled_nodes):
      print()
      print("All nodes are labeled ones")
      break 
    print("---------------------------------------------------------------------")
    i = i+1
  print ("============================================")
  print ("Learned Best GDL program")
  print (new_GDL_program.nodeVars)
  print (new_GDL_program.edgeVars)
  print ("============================================")
  return (new_GDL_programs, new_GDL_program)






def specify(GDL_program, data):
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


def specify_binary(GDL_program, data):
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
            continue
          else:
            bot = 0.5 
            top = 1
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
            bot = 0.0
            top = 0.5
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


      if len(GDL_program.nodeVars) < 3:
        for j in range(len(data.X_node[0])):
          new_node = {}
          bot = 0.5 
          top = 1
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
          bot = 0.0
          top = 0.5
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
          bot = 0.5
          top = 1.0
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
          bot = 0.0
          top = 0.5
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






