import pickle
import argparse
import json
from language import *
#from top_down_synthesis_NC import *
from data_loader import *
import datetime
from util import search_hyperparameters, find_max_0
from store_predictions import store_predictions

def k_hop_subgraph_nodes (data, dataset, test_node):
  nodes = set([test_node])
  edges = set()
  if dataset in ['BA-shapes', 'Tree-cycles']:
    k = 3
  else:
    k = 2
  for i in range(k):
    tmp_nodes = copy.deepcopy(nodes)
    for _, node in enumerate(nodes):
      succ_nodes = data.succ_node_to_nodes[node]
      pred_nodes = data.pred_node_to_nodes[node]
      adj_nodes = succ_nodes | pred_nodes
      for _, adj_node in enumerate(adj_nodes):
        if not adj_node in tmp_nodes:
          tmp_nodes.add(adj_node)
        if not (node, adj_node) in edges:
          if not (adj_node, node) in edges:
            edges.add( (node, adj_node) )
    nodes = tmp_nodes
  return nodes

def eval_acc_explainability(dataset):
  data = data_loader(dataset)

  label_len = len(data.label_to_nodes)
  print(label_len)
  val_test_nodes = data.val_nodes | data.test_nodes
  
  print("=======================================================")
  (default_label, fitted_label, amplify, val_threshold) = search_hyperparameters(data, dataset)
  print("=======================================================")
  print("Default label : {}".format(default_label))
  print("Fitted label : {}".format(fitted_label))
  print("Amplify : {}".format(amplify))
  print("Val threshold : {}".format(val_threshold))  
  default_GDL_pgm = GDL()
  default_GDL_pgm.nodeVars = [{}]
  default_GDL_pgm.edgeVars = []
  chosen_nodes = eval_GDL_program_NC_DFS(default_GDL_pgm, data)

  GDL_program_sets = []
  for i in range(len(data.label_to_nodes)):
    GDL_program_sets.append(set())

  print(GDL_program_sets)
  
  test_node_to_scores = {}
  for _, test_node in enumerate(data.test_nodes):
    test_node_to_scores[test_node] = []
    for label in range(label_len):
      test_node_to_scores[test_node].append((-1, None))
    test_node_to_scores[test_node][default_label] = (0.0, default_GDL_pgm)
  
  for my_label in range(label_len):
    print("Processing label {}".format(my_label))
    with open('datasets/{}/learned_GDL_programs/td/learned_GDL_programs_for_label_{}.pickle'.format(dataset, my_label), 'rb') as f:
      learned_tuples_set = pickle.load(f) 
    check_redundant_GDL_program = set()
    print()
    print("Label : {}".format(my_label))
    print()
    for _, learned_tuple in enumerate(learned_tuples_set):
      label = learned_tuple[0]
      learned_GDL_pgm = learned_tuple[1]
      score = learned_tuple[2]
      chosen_nodes = learned_tuple[3]
      key = (json.dumps(learned_GDL_pgm.nodeVars), json.dumps(learned_GDL_pgm.edgeVars))
      if key in check_redundant_GDL_program:
        continue
      else:
        check_redundant_GDL_program.add(key)
      chosen_val_test_nodes = chosen_nodes & val_test_nodes
      chosen_val_nodes = chosen_nodes & data.val_nodes
      if len(chosen_val_nodes) < val_threshold:
        continue
      if label == fitted_label:
        score = score * amplify
      
      GDL_program_sets[my_label].add((score, learned_GDL_pgm))
        
      for _, test_node in enumerate(chosen_nodes & data.test_nodes):
        if test_node_to_scores[test_node][label][0] < score:
          test_node_to_scores[test_node][label] = (score, learned_GDL_pgm)
      
  fidelity_sum = []
  sparsity_sum = []

  generality_sum = []
  precision_sum = []

  with open("predicted/{}_predicted.pickle".format(dataset), 'rb') as f:
    node_predictions = pickle.load(f)

  accurately_classified_nodes = 0
  for _, node in enumerate(data.test_nodes):
    my_GDL_programs_scores = copy.deepcopy(test_node_to_scores[node])
    prediction = find_max_0(test_node_to_scores[node])
    if test_node_to_scores[node][prediction][0] > 0.1:
      provided_GDL_program = test_node_to_scores[node][prediction][1]
      matching_subgraph = find_matching_subgraph_NC(provided_GDL_program, data, node)
      original_nodes = k_hop_subgraph_nodes(data, dataset, node)
      important_nodes = set(copy.deepcopy(matching_subgraph[0]))
      sparsity_score = 1 - (len(important_nodes) / len(original_nodes))
      sparsity_sum.append(sparsity_score)

      for my_label in range(len(data.label_to_nodes)):
        if my_label == prediction:
          continue
        else:
          for _, score_pgm in enumerate(GDL_program_sets[my_label]):
            score = score_pgm[0]
            new_GDL_program = score_pgm[1]
            chosen_nodes = eval_GDL_program_NC_DFS(new_GDL_program, data) 
            if node in chosen_nodes:
              chosen_train_nodes = chosen_nodes & data.train_nodes
              correctly_chosen_train_nodes = chosen_nodes & data.train_nodes & data.label_to_nodes[my_label]
              score = float(len(correctly_chosen_train_nodes) / (len(chosen_train_nodes) + data.epsilon))
              if my_label == fitted_label:
                score = score * amplify
              if score > test_node_to_scores[node][prediction][0]:
                fidelity_sum.append(1)    
                #print("Cannot be happened")
                #raise 
      
      fidelity_sum.append(0)
      chosen_nodes = eval_GDL_program_NC_DFS(provided_GDL_program, data) 
      correctly_explained_predictions = chosen_nodes & node_predictions[prediction]
      generality = len(correctly_explained_predictions)/len(node_predictions[prediction])
      precision = len(correctly_explained_predictions)/len(chosen_nodes) 
      
      print()
      print()
      print("============================================================")
      print("Test node : {}".format(node))
      print()
      print()
      print_GDL_program(provided_GDL_program, 'normal')
      print("Sparsity : {}".format(sparsity_score))
      print("Fidelity : {}".format(0))
      print("Generality : {}".format(generality))
      print("Precision : {}".format(precision))
      print("============================================================")
      #print(node_predictions)
      
      generality_sum.append(generality)
      precision_sum.append(precision)
    if prediction == data.node_to_label[node]:
      accurately_classified_nodes = accurately_classified_nodes + 1
  accuracy = float(accurately_classified_nodes/len(data.test_nodes))
  print()
  print("==============================================================")
  print("Test Nodes : {}".format(len(data.test_nodes)))
  print("Accurately Classified Nodes : {}".format(accurately_classified_nodes))
  print("Accuracy : {}".format(accuracy))
  print("==============================================================")
  
  print("Fidelity : {}".format((sum(fidelity_sum) / len(fidelity_sum))))
  print("Sparsity : {}".format((sum(sparsity_sum) / len(sparsity_sum))))
  print("Generality : {}".format((sum(generality_sum) / len(generality_sum))))
  print("Precision : {}".format((sum(precision_sum) / len(precision_sum)))) 
  #print(sparsity_sum) 


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', '--dataset', help="input dataset")
  #parser.add_argument('-e', '--epsilon', help="input epsilon")
  args = parser.parse_args()
  dataset = args.dataset
  #epsilon = float(args.epsilon)
  store_predictions(dataset)
  print("Stored predictions")
  eval_acc_explainability(dataset)
