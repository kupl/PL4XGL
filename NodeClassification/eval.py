import pickle
import argparse
import json
from language import *
#from top_down_synthesis_NC import *
from data_loader import *
from util import search_hyperparameters, find_max_0
import datetime



def evaluate(dataset):
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
        
      for _, test_node in enumerate(chosen_nodes & data.test_nodes):
        if test_node_to_scores[test_node][label][0] < score:
          test_node_to_scores[test_node][label] = (score, learned_GDL_pgm)
      
      
  accurately_classified_nodes = 0
  for _, node in enumerate(data.test_nodes):
    prediction = find_max_0(test_node_to_scores[node])
    if prediction == data.node_to_label[node]:
      accurately_classified_nodes = accurately_classified_nodes + 1
      
  #print(test_node_to_scores)
  accuracy = float(accurately_classified_nodes/len(data.test_nodes))
  print()
  print("==============================================================")
  print("Test Nodes : {}".format(len(data.test_nodes)))
  print("Accurately Classified Nodes : {}".format(accurately_classified_nodes))
  print("Accuracy : {}".format(accuracy))
  print("==============================================================")
  
  
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', '--dataset', help="input dataset")
  args = parser.parse_args()
  dataset = args.dataset
  start = datetime.datetime.now()   
  evaluate(dataset)
  finish = datetime.datetime.now()
  elapsed = finish - start
  print("Elapsed time: {}".format(elapsed))
  
