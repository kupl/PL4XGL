from language import *
from synthesis.specify_middle import specify_middle
from synthesis.specify_mean import specify_mean
from synthesis.score import score
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
      (new_GDL_program, new_score) = specify_mean(current_GDL_program, data)
    else:
      (new_GDL_program, new_score) = specify_middle(current_GDL_program, data)
    
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


