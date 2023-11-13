from jargon import *
from language import *
import copy
import json
import sys


def sentences_to_GDL_programs(sentences_set, data):
  GDL_programs = set()
  for _, sentence in enumerate(sentences_set):
    variables = sentence.absList
    root = sentence.root
    pgm = GDL()
    sentence_len = len(variables)
    if sentence_len == 1:
      pgm.nodeVars.append(variables[0])
    elif sentence_len == 2:
      pgm.nodeVars.append(variables[0])
      pgm.nodeVars.append(variables[1])
      pgm.edgeVars.append( ({},0,1) )

    elif sentence_len == 3:
      if root == 0:
        pgm.nodeVars.append(variables[0])
        pgm.nodeVars.append(variables[1])
        pgm.nodeVars.append(variables[2])
        pgm.edgeVars.append( ({},0,1) )
        pgm.edgeVars.append( ({},1,2) )

      elif root == 1:
        pgm.nodeVars.append(variables[1])
        pgm.nodeVars.append(variables[0])
        pgm.nodeVars.append(variables[2])
        pgm.edgeVars.append( ({},1,0) )
        pgm.edgeVars.append( ({},2,0) )

      else:
        raise Exception("NotImplemented")

    else:
      raise Exception("NotImplemented")
    if eval_GDL_program_NC_DFS(pgm, data) != eval_sentence(sentence, data.succ_node_to_nodes, data.pred_node_to_nodes, data.X_node):
      #print()
      #print()
      #print()
      #print(sentence.absList)
      #print(sentence.root)
      #print("------------")
      #print(pgm.nodeVars)
      #print(pgm.edgeVars)

      raise Exception("Cannot be happened")
    GDL_programs.add(pgm)
  return GDL_programs


def learn_sentences(data): 
  #data.is_complex_graph = True 
  print("Chosen_depth : {}".format(data.chosen_depth))
  i = 1 
  sentences = set()
  data.covered_nodes = set()
  print("labeled nodes : "+str(len(data.left_nodes)))
  print("COVERED nodes : "+str(len(data.covered_nodes)))
  print("ORIGINAL_LABELED_NODES nodes : "+str(len(data.original_labeled_nodes)))
  while(len(data.left_nodes)>0):
    print()
    print()
    print("Outer iteration : "+str(i))
    print ("")
    print ("--------------------------------------------")
    '''new_sentence = learn_a_sentence(node_to_nodes, X_node, labeled_nodes, data.feature_results)'''
    (new_sentences, new_sentence) = learn_a_sentence(data)
    print ("--------------------------------------------")
    print ("")
    print ("============================================")
    print ("Learned Best Sentence : "+str(new_sentence.absList))
    print ("Learned Best Sentence root : "+str(new_sentence.root))
    #chosen_nodes = filter_eval_sentence(new_sentence, data.node_to_nodes, data.X_node, data.original_labeled_nodes, data.original_labeled_nodes) & data.train_nodes
    chosen_nodes = eval_sentence(new_sentence, data.succ_node_to_nodes, data.pred_node_to_nodes, data.X_node) & data.train_nodes 
    print ("# of chosen Nodes : "+str(len((chosen_nodes & data.train_nodes))))
    print ("Chosen Labeled Nodes : "+str(chosen_nodes & data.original_labeled_nodes))
    print ("# of chosen Non Labeled Nodes : "+str(len((chosen_nodes - data.original_labeled_nodes))))
    data.covered_nodes = data.covered_nodes | (data.original_labeled_nodes & chosen_nodes)
    print ("COVERED nodes : "+str(len(data.covered_nodes)))
    print ("============================================")
    
    if len(chosen_nodes & data.original_labeled_nodes) == len(data.original_labeled_nodes):
      #Found a very good sentence
      print("Find a very good sentence")
      return set([new_sentence])

    #sentences.add(new_sentence)
    sentences = sentences | new_sentences 
    #sentences_to_GDL_programs(sentences, data)
    data.left_nodes = data.left_nodes - chosen_nodes 
    print("left nodes : "+str(len(data.left_nodes)))
    i = i+1
    if data.is_complex_graph and (len(data.left_nodes) < len(data.original_labeled_nodes) * 0.05):
      print("It is too complex graph, we stop learning here")
      #return sentences
      return sentences_to_GDL_programs(sentences, data)
  #return sentences
  return sentences_to_GDL_programs(sentences, data)



def learn_a_sentence(data):
  sentence = Sentence()
  sentence.root = 0 
  sentence.absList = [{}]
  
  current_sentence_score = -1.0
  new_sentence_score = 0.0
  current_sentence = sentence
  new_sentence = sentence
  new_sentences = set()
  i = 1
  data.filtered_nodes = data.train_nodes
  chosen_nodes = data.filtered_nodes
  while(new_sentence_score > current_sentence_score):
    sentences_to_GDL_programs(set([sentence]), data)
    current_sentence = new_sentence
    current_sentence_score = new_sentence_score
    print("")
    print("")
    print("---------------------------------------------------------------------")
    print("Inner iteration : "+str(i))
    if data.is_one_hot == True:
      #(new_sentence, new_sentence_score) = specify_binary(current_sentence, data)
      (new_sentence, new_sentence_score, my_sentences) = specify_binary(current_sentence, data)
    else:
      (new_sentence, new_sentence_score) = specify(current_sentence, data)
    
    new_sentences.add(new_sentence) 
    #new_sentences = new_sentences | my_sentences
    print("new_sentence : "+str(len(new_sentence.absList)))
    print("new_sentence root : "+str(new_sentence.root))
    print("new_sentence score : : "+str(new_sentence_score))
    chosen_nodes = eval_sentence(new_sentence, data.succ_node_to_nodes, data.pred_node_to_nodes , data.X_node) & data.train_nodes 
    data.filtered_nodes = chosen_nodes
    print("# of chosen Nodes : "+str(len(chosen_nodes)))
    print("Chosen Labeled Nodes : "+str(chosen_nodes & data.original_labeled_nodes))
    if len(chosen_nodes) == len(chosen_nodes & data.original_labeled_nodes):
      print()
      print("All nodes are labeled ones")
      break 
    print("---------------------------------------------------------------------")
    i = i+1

    if data.is_complex_graph and (new_sentence_score > 0.9):
      print ("============================================")
      print ("Learned Best Sentence : "+str(new_sentence.absList))
      print ("Learned Best Sentence root : "+str(new_sentence.root))
      print ("Learned Best score : "+str(new_sentence_score))
      print ("============================================")
      return (new_sentences, new_sentence)

    if data.is_complex_graph :
      new_sentences_len_sum = 0
      for i in range(len(new_sentence.absList)):
        new_sentences_len_sum = new_sentences_len_sum + len(new_sentence.absList[i])
     
      if data.is_one_hot == True and new_sentences_len_sum >=3:
        return (new_sentences, new_sentence)
       

  print ("============================================")
  print ("Learned Best Sentence : "+str(new_sentence.absList))
  print ("Learned Best Sentence root : "+str(new_sentence.root))
  print ("Learned Best score : "+str(new_sentence_score))
  print ("============================================")
  return (new_sentences, new_sentence)

def specify(sentence, data):
  (best_score, _) = score(sentence, data)
  best_sentence = sentence
  print ("Curret Best sentence : " + str(best_sentence.absList))
  print ("Curret Best score : " + str(best_score))

  print ("sentence len : " + str(len(sentence.absList)))
  print ("features len : " + str(len(data.X_node[0])))
  candidate_sentences = set([sentence]) 
  for depth in range(data.chosen_depth):
    print()
    print("=====================================")
    print("Depth : {}".format(depth))
    print("=====================================")
    print()
    new_candidate_sentences = set()
    for _, sentence in enumerate(candidate_sentences): 
    
      for i in range(len(sentence.absList)):
        for j in range(len(data.X_node[0])):
          abs_node = sentence.absList[i]
          if j in abs_node:
            bot = abs_node[j][0]
            top = abs_node[j][1]
            top_idx = data.feature_list.index(top)
            #bot_idx = data.feature_list.index(bot)

            bot_idx = data.feature_list2.index(bot)
            bot_idx = len(data.feature_list) - bot_idx
            #if top_idx == bot_idx + 1:
            #  continue
            new_sentence = copy.deepcopy(sentence)
            #if top_idx == bot_idx + 1 :
            if data.feature_list[top_idx -1] == bot :
              #print("adj")
              new_sentence.absList[i][j] = (bot, bot)
            else:
              new_sentence.absList[i][j] = (bot, data.feature_list[int((top_idx+bot_idx)/2)])
              
            (new_score,_) = score(new_sentence, data)
            if depth < data.chosen_depth-1:
              new_candidate_sentences.add(new_sentence)
            if (new_score > best_score):
              best_score = new_score
              best_sentence = new_sentence
              print ("Current Best sentence : " + str(best_sentence.absList))
              print ("Current Best score : " + str(best_score))
              #sys.exit()
              

            new_sentence = copy.deepcopy(sentence)
            
            #if top_idx == bot_idx + 1 :
            if data.feature_list[top_idx -1] == bot :
              #print("adj")
              new_sentence.absList[i][j] = (top, top)
            else:
              new_sentence.absList[i][j] = (data.feature_list[int((top_idx+bot_idx)/2)], top)
            (new_score,_) = score(new_sentence, data)
            if depth < data.chosen_depth-1:
              new_candidate_sentences.add(new_sentence)
            if (new_score > best_score):
              best_score = new_score
              best_sentence = new_sentence
              print ("Current Best sentence : " + str(best_sentence.absList))
              print ("Current Best score : " + str(best_score))
          else: 
            print(data.min_max_feature)
            print(data.min_max_feature[0])
            print(data.min_max_feature[0][1])
            top = data.min_max_feature[0][1] 
            bot = data.feature_list[int(len(data.feature_list)/2)] 
            new_sentence = copy.deepcopy(sentence)
            new_sentence.absList[i][j] = (bot, top)
            (new_score, _) = score(new_sentence, data)
            if depth < data.chosen_depth-1:
              new_candidate_sentences.add(new_sentence)
            '''if (new_score >= best_score):'''
            if (new_score > best_score):
              best_score = new_score
              best_sentence = new_sentence
              print ("Current Best sentence : " + str(best_sentence.absList))
              print ("Current Best score : " + str(best_score))
            #bot = 0.0
            bot = data.min_max_feature[0][0] 
            top = data.feature_list[int(len(data.feature_list)/2)] 
            new_sentence = copy.deepcopy(sentence)
            new_sentence.absList[i][j] = (bot, top)
            (new_score, _) = score(new_sentence, data)
            if depth < data.chosen_depth-1:
              new_candidate_sentences.add(new_sentence)
            '''if (new_score >= best_score):'''
            if (new_score > best_score):
              best_score = new_score
              best_sentence = new_sentence
              print ("Current Best sentence : " + str(best_sentence.absList))
              print ("Current Best score : " + str(best_score))
      if len(sentence.absList) < 3:
        for j in range(len(data.X_node[0])):
          new_node = {}
          bot = data.feature_list[int(len(data.feature_list)/2)] 
          top = data.min_max_feature[0][1] 
          #top = 1
          new_node[j] = (bot,top)
          new_sentence = copy.deepcopy(sentence)
          new_sentence.absList.append(new_node)
          (new_score, _) = score(new_sentence, data)
          if depth < data.chosen_depth-1:
            new_candidate_sentences.add(new_sentence)
          '''if (new_score >= best_score):'''
          if (new_score > best_score):
            best_score = new_score
            best_sentence = new_sentence
            print ("Current Best sentence : " + str(best_sentence.absList))
            print ("Current Best score : " + str(best_score))

          new_node = {}
          #bot = 0.0 
          bot = data.min_max_feature[0][0] 
          top = data.feature_list[int(len(data.feature_list)/2)] 
          new_node[j] = (bot, top)
          new_sentence = copy.deepcopy(sentence)
          new_sentence.absList.append(new_node)
          (new_score, _) = score(new_sentence, data)
          if depth < data.chosen_depth-1:
            new_candidate_sentences.add(new_sentence)
          '''if (new_score >= best_score):'''
          if (new_score > best_score):
            best_score = new_score
            best_sentence = new_sentence
            print ("Current Best sentence : " + str(best_sentence.absList))
            print ("Current Best score : " + str(best_score))



        for j in range(len(data.X_node[0])):
          new_node = {}
          bot = data.feature_list[int(len(data.feature_list)/2)] 
          top = data.min_max_feature[0][1] 
          #top = 1.0
          new_node[j] = (bot,top)
          new_sentence = copy.deepcopy(sentence)
          new_sentence.absList.insert(0,new_node)
          new_sentence.root = new_sentence.root+1 
          (new_score, _) = score(new_sentence, data)
          if depth < data.chosen_depth-1:
            new_candidate_sentences.add(new_sentence)
          '''if (new_score >= best_score):'''
          if (new_score > best_score):
            best_score = new_score
            best_sentence = new_sentence
            print ("Current Best sentence : " + str(best_sentence.absList))
            print ("Current Best score : " + str(best_score))


          new_node = {}
          #bot = 0.0 
          bot = data.min_max_feature[0][0] 
          top = data.feature_list[int(len(data.feature_list)/2)] 
          new_node[j] = (bot,top)
          new_sentence = copy.deepcopy(sentence)
          new_sentence.absList.insert(0,new_node)
          new_sentence.root = new_sentence.root+1 
          (new_score, _) = score(new_sentence, data)
          if depth < data.chosen_depth-1:
            new_candidate_sentences.add(new_sentence)
          '''if (new_score >= best_score):'''
          if (new_score > best_score):
            best_score = new_score
            best_sentence = new_sentence
            print ("Current Best sentence : " + str(best_sentence.absList))
            print ("Current Best score : " + str(best_score))
    candidate_sentences = new_candidate_sentences
  print ("The Best sentence's list : " + str(best_sentence.absList))
  print ("The Best sentence's root : " + str(best_sentence.root))
  print ("The Best sentence's score : " + str(best_score))
  return (best_sentence, best_score) 



def specify_binary(sentence, data):
  #best_score = score(sentence, data)
  (best_score,_) = score(sentence, data)
  best_sentence = sentence
  print ("Curret Best sentence : " + str(best_sentence.absList))
  print ("Curret Best score : " + str(best_score))
  my_sentences = set()
  print ("sentence len : " + str(len(sentence.absList)))
  print ("features len : " + str(len(data.X_node[0])))
  candidate_sentences = set([sentence]) 
  for depth in range(data.chosen_depth):
    print()
    print("=====================================")
    print("Depth : {}".format(depth))
    print("=====================================")
    print()
    new_candidate_sentences = set()
    for _, sentence in enumerate(candidate_sentences): 
      for i in range(len(sentence.absList)):
        '''
        if i == sentence.root:
          feat_set = data.features[0]
        elif i == (len(sentence.absList) - sentence.root + 1) or i == (len(sentence.absList) - sentence.root - 1):
          feat_set = data.features[1]
        else : 
          feat_set = data.features[2]
        for _, j in enumerate(feat_set):
        '''
        for j in range(len(data.X_node[0])):
          abs_node = sentence.absList[i]
          if j in abs_node:
            continue
          else:
            bot = 0.5 
            top = 1
            new_sentence = copy.deepcopy(sentence)
            new_sentence.absList[i][j] = (bot, top)
            #new_score = score(new_sentence, data)
            (new_score1, new_score2) = score(new_sentence, data)
            if depth < data.chosen_depth-1:
              new_candidate_sentences.add(new_sentence)
            if (new_score1 > best_score):
              best_score = new_score1
              best_sentence = new_sentence
              print ("Current Best sentence : " + str(best_sentence.absList))
              print ("Current Best score : " + str(best_score))
            if new_score2 > 0.9:
              my_sentences.add(new_sentence)
            bot = 0.0
            top = 0.5
            new_sentence = copy.deepcopy(sentence)
            new_sentence.absList[i][j] = (bot, top)
            (new_score1, new_score2) = score(new_sentence, data)
            if depth < data.chosen_depth-1:
              new_candidate_sentences.add(new_sentence)
            if (new_score1 > best_score):
              best_score = new_score1
              best_sentence = new_sentence
              print ("Current Best sentence : " + str(best_sentence.absList))
              print ("Current Best score : " + str(best_score))
            if new_score2 > 0.9:
              my_sentences.add(new_sentence)
      #'''
      if len(sentence.absList) < 3:
        '''
        if len(sentence.absList) == 1:
          feat_set = data.features[1]
        if len(sentence.absList) == 2 and sentence.root == 1:
          feat_set = data.features[1]
        if len(sentence.absList) == 2 and sentence.root == 0:
          feat_set = data.features[2]
        for _, j in enumerate(feat_set):
        '''  
        for j in range(len(data.X_node[0])):
          new_node = {}
          bot = 0.5 
          top = 1
          new_node[j] = (bot,top)
          new_sentence = copy.deepcopy(sentence)
          new_sentence.absList.append(new_node)
          #new_score = score(new_sentence, data)
          (new_score1, new_score2) = score(new_sentence, data)
          if depth < data.chosen_depth-1:
            new_candidate_sentences.add(new_sentence)
          if (new_score1 > best_score):
            best_score = new_score1
            best_sentence = new_sentence
            print ("Current Best sentence : " + str(best_sentence.absList))
            print ("Current Best score : " + str(best_score))
          if new_score2 > 0.9:
            my_sentences.add(new_sentence)
          #print()
          #print("New sentence")
          #print(new_sentence.absList)
          #print(new_sentence.root)
          #print(new_score1)
          #print(new_score2)
          #print()
          new_node = {}
          bot = 0.0 
          top = 0.5 
          new_node[j] = (bot, top)
          new_sentence = copy.deepcopy(sentence)
          new_sentence.absList.append(new_node)
          #new_score = score(new_sentence, data)
          (new_score1, new_score2) = score(new_sentence, data)
          if depth < data.chosen_depth-1:
            new_candidate_sentences.add(new_sentence)
          if (new_score1 > best_score):
            best_score = new_score1
            best_sentence = new_sentence
            print ("Current Best sentence : " + str(best_sentence.absList))
            print ("Current Best score : " + str(best_score))
          if new_score2 > 0.9:
            my_sentences.add(new_sentence)

        '''
        if len(sentence.absList) == 1:
          feat_set = data.features[1]
        if len(sentence.absList) == 2 and sentence.root == 0:
          feat_set = data.features[1]
        if len(sentence.absList) == 2 and sentence.root == 1:
          feat_set = data.features[2]
        for _, j in enumerate(feat_set):
        '''


        for j in range(len(data.X_node[0])):
          new_node = {}
          bot = 0.5 
          top = 1.0
          new_node[j] = (bot,top)
          new_sentence = copy.deepcopy(sentence)
          new_sentence.absList.insert(0,new_node)
          new_sentence.root = new_sentence.root+1 
          #new_score = score(new_sentence, data)
          (new_score1, new_score2) = score(new_sentence, data)
          if depth < data.chosen_depth-1:
            new_candidate_sentences.add(new_sentence)
          if (new_score1 > best_score):
            best_score = new_score1
            best_sentence = new_sentence
            print ("Current Best sentence : " + str(best_sentence.absList))
            print ("Current Best score : " + str(best_score))
          if new_score2 > 0.9:
            my_sentences.add(new_sentence)

          new_node = {}
          bot = 0.0 
          top = 0.5
          new_node[j] = (bot,top)
          new_sentence = copy.deepcopy(sentence)
          new_sentence.absList.insert(0,new_node)
          new_sentence.root = new_sentence.root+1 
          #new_score = score(new_sentence, data)
          (new_score1, new_score2) = score(new_sentence, data)
          if depth < data.chosen_depth-1:
            new_candidate_sentences.add(new_sentence)
          if (new_score1 > best_score):
            best_score = new_score1
            best_sentence = new_sentence
            print ("Current Best sentence : " + str(best_sentence.absList))
            print ("Current Best score : " + str(best_score))
          if new_score2 > 0.9:
            my_sentences.add(new_sentence)
      #'''
    candidate_sentences = new_candidate_sentences
  print ("The Best sentence's list : " + str(best_sentence.absList))
  print ("The Best sentence's root : " + str(best_sentence.root))
  print ("The Best sentence's score : " + str(best_score))
  return (best_sentence, best_score, my_sentences) 




def score(sentence, data):
  key = (sentence.root, json.dumps(sentence.absList))
  if key in data.dict:
    nodes = data.dict[key]
  else:  
    nodes = filter_eval_sentence(sentence, data.succ_node_to_nodes, data.pred_node_to_nodes, data.X_node, data.filtered_nodes)
    data.dict[key] = nodes
 
  #print()
  #print("Sentence : {}".format(sentence.absList))
  #print("Node Len : {}".format(len(nodes)))
  nodes = nodes & data.train_nodes
  #print("Score : {}".format(score))
  #score = float(len(data.original_labeled_nodes & nodes)) / float(len(nodes)+0.1)
  #score = float(len(data.original_labeled_nodes & nodes)) / float(len(nodes)+0.1)
  #score = float(len(data.original_labeled_nodes & nodes)) / float(len(nodes)+0.1)
  #score = float(len(data.original_labeled_nodes & nodes)) / float(len(nodes)+10)
  score = float(len(data.original_labeled_nodes & nodes)) / float(len(nodes) + data.epsilon)
  if len(data.left_nodes & nodes) == 0:  
    return (0.001, score)
  else:
    return (score, score)
  #return float(len(data.original_labeled_nodes & nodes)) / float(len(nodes)+0.1)






